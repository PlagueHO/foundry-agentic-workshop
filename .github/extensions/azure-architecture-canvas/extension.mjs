import { createServer } from 'node:http';
import { existsSync } from 'node:fs';
import { readFile } from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { CanvasError, createCanvas, joinSession } from '@github/copilot-sdk/extension';

const DEFAULT_BICEP_PATH = path.join('infra', 'main.bicep');
const DEFAULT_BICEPPARAM_PATH = path.join('infra', 'main.bicepparam');

const MODULE_DECLARATION_REGEX =
    /^\s*module\s+([A-Za-z_][A-Za-z0-9_]*)\s+'([^']+)'\s*=\s*(?:if\s*\((.+)\)\s*)?([\[{])/;
const PARAMETER_ASSIGNMENT_REGEX = /^\s*param\s+([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.+?)\s*$/;
const EXTENSION_DIRECTORY = path.dirname(fileURLToPath(import.meta.url));
const PROJECT_ROOT = path.resolve(EXTENSION_DIRECTORY, '..', '..', '..');

/** @type {Map<string, { server: import('node:http').Server, url: string, documentKey: string }>} */
const instances = new Map();
/** @type {Map<string, CanvasDocument>} */
const documents = new Map();

function normalizePathForComparison(value) {
    return path.normalize(value).replace(/[\\/]+$/, '').toLowerCase();
}

function isPathInsideRoot(candidatePath, rootPath) {
    const normalizedWorkspace = normalizePathForComparison(rootPath);
    const normalizedCandidate = normalizePathForComparison(candidatePath);
    const workspacePrefix = `${normalizedWorkspace}${path.sep}`;

    return normalizedCandidate === normalizedWorkspace || normalizedCandidate.startsWith(workspacePrefix);
}

function assertPathInsideRoots(candidatePath, candidateRoots) {
    if (candidateRoots.some((rootPath) => isPathInsideRoot(candidatePath, rootPath))) {
        return;
    }

    throw new CanvasError(
        'canvas_input_invalid',
        `Path "${candidatePath}" must be inside one of the allowed roots.`
    );
}

function getCandidateRoots(workspacePath) {
    const roots = [workspacePath, PROJECT_ROOT, process.cwd()]
        .filter((value) => typeof value === 'string' && value.trim().length > 0)
        .map((value) => path.resolve(value));

    return [...new Set(roots)];
}

function decodeBicepString(value) {
    return value.replace(/''/g, "'");
}

function parseBooleanExpression(expression) {
    const match = expression.match(
        /^toLower\(readEnvironmentVariable\('([^']+)'\s*,\s*'([^']*)'\)\)\s*(==|!=)\s*'([^']+)'\s*$/
    );
    if (!match) {
        return null;
    }

    const [, envVar, defaultValue, operator, rightOperand] = match;
    const normalizedDefault = decodeBicepString(defaultValue).toLowerCase();
    const normalizedRight = decodeBicepString(rightOperand).toLowerCase();

    return {
        type: 'bool',
        envVar,
        defaultValue: operator === '==' ? normalizedDefault === normalizedRight : normalizedDefault !== normalizedRight,
    };
}

function parseIntegerExpression(expression) {
    const match = expression.match(/^int\(readEnvironmentVariable\('([^']+)'\s*,\s*'([^']*)'\)\)\s*$/);
    if (!match) {
        return null;
    }

    const [, envVar, defaultValue] = match;
    const parsed = Number.parseInt(decodeBicepString(defaultValue), 10);

    return {
        type: 'int',
        envVar,
        defaultValue: Number.isNaN(parsed) ? 0 : parsed,
    };
}

function parseJsonExpression(expression) {
    const match = expression.match(/^json\(readEnvironmentVariable\('([^']+)'\s*,\s*'([^']*)'\)\)\s*$/);
    if (!match) {
        return null;
    }

    const [, envVar, defaultValue] = match;
    const decoded = decodeBicepString(defaultValue);
    let parsed = [];
    try {
        parsed = JSON.parse(decoded);
    } catch {
        parsed = [];
    }

    return {
        type: 'json',
        envVar,
        defaultValue: parsed,
    };
}

function parseStringExpression(expression) {
    const match = expression.match(/^readEnvironmentVariable\('([^']+)'\s*,\s*'([^']*)'\)\s*$/);
    if (!match) {
        return null;
    }

    const [, envVar, defaultValue] = match;
    return {
        type: 'string',
        envVar,
        defaultValue: decodeBicepString(defaultValue),
    };
}

function parseParameterExpression(expression) {
    return (
        parseBooleanExpression(expression) ??
        parseIntegerExpression(expression) ??
        parseJsonExpression(expression) ??
        parseStringExpression(expression) ?? {
            type: 'string',
            envVar: null,
            defaultValue: expression,
        }
    );
}

/**
 * @param {string} content
 * @returns {CanvasParameter[]}
 */
function parseBicepparamParameters(content) {
    const parameters = [];
    for (const line of content.split(/\r?\n/)) {
        const trimmed = line.trim();
        if (!trimmed || trimmed.startsWith('//')) {
            continue;
        }

        const match = line.match(PARAMETER_ASSIGNMENT_REGEX);
        if (!match) {
            continue;
        }

        const [, name, expression] = match;
        const parsedExpression = parseParameterExpression(expression);
        parameters.push({
            name,
            type: parsedExpression.type,
            envVar: parsedExpression.envVar,
            expression,
            defaultValue: parsedExpression.defaultValue,
            value: structuredClone(parsedExpression.defaultValue),
        });
    }

    return parameters;
}

function stripComments(value) {
    return value
        .replace(/\/\/.*$/gm, '')
        .replace(/#disable-next-line.*$/gm, '')
        .trim();
}

function extractDependsOnBlock(blockText) {
    const match = blockText.match(/dependsOn\s*:\s*\[([\s\S]*?)\]/m);
    if (!match) {
        return [];
    }

    const cleaned = stripComments(match[1]);
    const dependencies = [];
    for (const depMatch of cleaned.matchAll(/\b([A-Za-z_][A-Za-z0-9_]*)\b/g)) {
        dependencies.push(depMatch[1]);
    }

    return [...new Set(dependencies)];
}

function titleFromModuleName(value) {
    return value
        .replace(/([a-z0-9])([A-Z])/g, '$1 $2')
        .replace(/([A-Z])([A-Z][a-z])/g, '$1 $2')
        .replace(/_/g, ' ')
        .replace(/\s+/g, ' ')
        .trim()
        .replace(/^./, (c) => c.toUpperCase());
}

function categoryFromModule(definition) {
    const lowerPath = definition.path.toLowerCase();
    const lowerName = definition.name.toLowerCase();

    if (lowerPath.includes('/security/') || lowerName.includes('role')) {
        return 'Security';
    }
    if (lowerPath.includes('/host/') || lowerName.includes('containerapps') || lowerName.includes('portal')) {
        return 'Hosting';
    }
    if (lowerName.includes('foundry') || lowerName.includes('cognitive')) {
        return 'Foundry';
    }
    if (lowerName.includes('search')) {
        return 'Search';
    }
    if (lowerName.includes('cosmos') || lowerName.includes('storage')) {
        return 'Data';
    }
    if (lowerName.includes('insights') || lowerName.includes('analytics')) {
        return 'Observability';
    }
    if (lowerName.includes('registry')) {
        return 'Registry';
    }

    return 'Core';
}

/**
 * @param {string} content
 * @returns {CanvasModule[]}
 */
function parseBicepModules(content) {
    const lines = content.split(/\r?\n/);
    const modules = [];

    for (let index = 0; index < lines.length; index += 1) {
        const startLine = lines[index];
        const startMatch = startLine.match(MODULE_DECLARATION_REGEX);
        if (!startMatch) {
            continue;
        }

        const [, name, modulePath, condition, openingToken] = startMatch;
        let braceDepth = 0;
        let bracketDepth = 0;
        let encounteredOpening = false;
        let endIndex = index;
        const closesOnBracket = openingToken === '[';

        for (let innerIndex = index; innerIndex < lines.length; innerIndex += 1) {
            const currentLine = lines[innerIndex];
            let inSingleQuote = false;
            for (const character of currentLine) {
                if (character === "'") {
                    inSingleQuote = !inSingleQuote;
                    continue;
                }

                if (inSingleQuote) {
                    continue;
                }

                if (character === '{') {
                    braceDepth += 1;
                    encounteredOpening = true;
                } else if (character === '}') {
                    braceDepth -= 1;
                } else if (character === '[') {
                    bracketDepth += 1;
                    encounteredOpening = true;
                } else if (character === ']') {
                    bracketDepth -= 1;
                }
            }

            endIndex = innerIndex;
            if (
                encounteredOpening &&
                ((closesOnBracket && bracketDepth === 0) || (!closesOnBracket && braceDepth === 0))
            ) {
                break;
            }
        }

        const blockText = lines.slice(index, endIndex + 1).join('\n');
        modules.push({
            id: name,
            name,
            title: titleFromModuleName(name),
            path: modulePath,
            category: categoryFromModule({ name, path: modulePath }),
            condition: condition?.trim() ?? null,
            rawDependsOn: extractDependsOnBlock(blockText),
        });

        index = endIndex;
    }

    const moduleNames = new Set(modules.map((module) => module.name));
    for (const module of modules) {
        module.dependsOn = module.rawDependsOn.filter((dependency) => moduleNames.has(dependency));
    }

    return modules;
}

function stripOuterParentheses(value) {
    let text = value.trim();
    let changed = true;
    while (changed && text.startsWith('(') && text.endsWith(')')) {
        changed = false;
        let depth = 0;
        for (let index = 0; index < text.length; index += 1) {
            const character = text[index];
            if (character === '(') {
                depth += 1;
            } else if (character === ')') {
                depth -= 1;
                if (depth === 0 && index < text.length - 1) {
                    return text;
                }
            }
        }

        if (depth === 0) {
            text = text.slice(1, -1).trim();
            changed = true;
        }
    }

    return text;
}

function splitTopLevelByOperator(expression, operator) {
    const parts = [];
    let depth = 0;
    let inSingleQuote = false;
    let segmentStart = 0;

    for (let index = 0; index < expression.length; index += 1) {
        const character = expression[index];
        if (character === "'") {
            inSingleQuote = !inSingleQuote;
            continue;
        }

        if (inSingleQuote) {
            continue;
        }

        if (character === '(') {
            depth += 1;
            continue;
        }

        if (character === ')') {
            depth -= 1;
            continue;
        }

        if (
            depth === 0 &&
            expression[index] === operator[0] &&
            expression[index + 1] === operator[1]
        ) {
            parts.push(expression.slice(segmentStart, index).trim());
            segmentStart = index + 2;
            index += 1;
        }
    }

    if (segmentStart === 0) {
        return [expression.trim()];
    }

    parts.push(expression.slice(segmentStart).trim());
    return parts.filter((part) => part.length > 0);
}

function isValueEmpty(value) {
    if (value === null || value === undefined) {
        return true;
    }
    if (typeof value === 'string') {
        return value.trim().length === 0;
    }
    if (Array.isArray(value)) {
        return value.length === 0;
    }
    if (typeof value === 'object') {
        return Object.keys(value).length === 0;
    }
    return false;
}

function buildEvaluationContext(parametersByName) {
    const resolvedAttendeeList = parametersByName.resolvedAttendeeList;
    const resolvedAttendeesWithIds = Array.isArray(resolvedAttendeeList)
        ? resolvedAttendeeList.filter(
              (entry) =>
                  entry &&
                  typeof entry === 'object' &&
                  !isValueEmpty(entry.objectId)
          )
        : [];

    return {
        ...parametersByName,
        resolvedAttendeesWithIds,
    };
}

function resolveIdentifierValue(identifier, contextValues) {
    const trimmed = identifier.trim();
    if (Object.hasOwn(contextValues, trimmed)) {
        return contextValues[trimmed];
    }
    return undefined;
}

function evaluateConditionExpression(expression, contextValues) {
    const expr = stripOuterParentheses(expression);
    const orSegments = splitTopLevelByOperator(expr, '||');
    if (orSegments.length > 1) {
        return orSegments.some((segment) => evaluateConditionExpression(segment, contextValues));
    }

    const andSegments = splitTopLevelByOperator(expr, '&&');
    if (andSegments.length > 1) {
        return andSegments.every((segment) => evaluateConditionExpression(segment, contextValues));
    }

    const notEmptyMatch = expr.match(/^!empty\((.+)\)$/);
    if (notEmptyMatch) {
        const value = resolveIdentifierValue(notEmptyMatch[1], contextValues);
        return !isValueEmpty(value);
    }

    const emptyMatch = expr.match(/^empty\((.+)\)$/);
    if (emptyMatch) {
        const value = resolveIdentifierValue(emptyMatch[1], contextValues);
        return isValueEmpty(value);
    }

    const comparisonMatch = expr.match(/^([A-Za-z_][A-Za-z0-9_]*)\s*(==|!=)\s*'([^']*)'$/);
    if (comparisonMatch) {
        const [, identifier, operator, literalValue] = comparisonMatch;
        const leftValue = String(resolveIdentifierValue(identifier, contextValues) ?? '');
        const rightValue = decodeBicepString(literalValue);
        return operator === '==' ? leftValue === rightValue : leftValue !== rightValue;
    }

    if (expr.startsWith('!')) {
        return !evaluateConditionExpression(expr.slice(1).trim(), contextValues);
    }

    if (/^[A-Za-z_][A-Za-z0-9_]*$/.test(expr)) {
        return Boolean(resolveIdentifierValue(expr, contextValues));
    }

    return true;
}

/**
 * @param {CanvasModule[]} modules
 * @param {Record<string, unknown>} parametersByName
 */
function buildArchitectureGraph(modules, parametersByName) {
    const contextValues = buildEvaluationContext(parametersByName);

    const nodes = modules.map((module) => {
        const active = module.condition
            ? evaluateConditionExpression(module.condition, contextValues)
            : true;
        return {
            id: module.id,
            label: module.title,
            name: module.name,
            category: module.category,
            path: module.path,
            condition: module.condition,
            active,
            dependsOn: module.dependsOn,
        };
    });

    const edges = [];
    for (const module of modules) {
        for (const dependency of module.dependsOn) {
            edges.push({
                from: dependency,
                to: module.name,
            });
        }
    }

    return {
        nodes,
        edges,
        activeCount: nodes.filter((node) => node.active).length,
        inactiveCount: nodes.filter((node) => !node.active).length,
    };
}

function coerceParameterValue(parameter, rawValue) {
    switch (parameter.type) {
        case 'bool':
            if (typeof rawValue === 'boolean') {
                return rawValue;
            }
            if (typeof rawValue === 'string') {
                const normalized = rawValue.trim().toLowerCase();
                if (normalized === 'true') {
                    return true;
                }
                if (normalized === 'false') {
                    return false;
                }
            }
            throw new CanvasError('canvas_input_invalid', `Parameter "${parameter.name}" must be a boolean.`);
        case 'int':
            if (typeof rawValue === 'number' && Number.isFinite(rawValue)) {
                return Math.trunc(rawValue);
            }
            if (typeof rawValue === 'string' && rawValue.trim().length > 0) {
                const parsed = Number.parseInt(rawValue.trim(), 10);
                if (!Number.isNaN(parsed)) {
                    return parsed;
                }
            }
            throw new CanvasError('canvas_input_invalid', `Parameter "${parameter.name}" must be an integer.`);
        case 'json':
            if (typeof rawValue === 'string') {
                try {
                    return JSON.parse(rawValue);
                } catch {
                    throw new CanvasError('canvas_input_invalid', `Parameter "${parameter.name}" must be valid JSON.`);
                }
            }
            if (rawValue === null || rawValue === undefined) {
                return null;
            }
            return rawValue;
        case 'string':
        default:
            if (rawValue === null || rawValue === undefined) {
                return '';
            }
            return String(rawValue);
    }
}

function parametersToMap(parameters) {
    /** @type {Record<string, unknown>} */
    const result = {};
    for (const parameter of parameters) {
        result[parameter.name] = parameter.value;
    }
    return result;
}

function applyParameterValues(document, updates) {
    for (const parameter of document.parameters) {
        if (!Object.hasOwn(updates, parameter.name)) {
            continue;
        }

        parameter.value = coerceParameterValue(parameter, updates[parameter.name]);
    }

    document.graph = buildArchitectureGraph(document.modules, parametersToMap(document.parameters));
}

function resetParameterValues(document) {
    for (const parameter of document.parameters) {
        parameter.value = structuredClone(parameter.defaultValue);
    }
    document.graph = buildArchitectureGraph(document.modules, parametersToMap(document.parameters));
}

function createDocumentResponse(document) {
    return {
        title: 'Azure Architecture from Bicep',
        files: {
            bicepPath: document.bicepPath,
            bicepparamPath: document.bicepparamPath,
        },
        parameters: document.parameters.map((parameter) => ({
            name: parameter.name,
            type: parameter.type,
            envVar: parameter.envVar,
            expression: parameter.expression,
            defaultValue: parameter.defaultValue,
            value: parameter.value,
        })),
        graph: document.graph,
        updatedAt: document.updatedAt,
    };
}

async function loadDocument(config, preservedValues) {
    let bicepContent;
    let bicepparamContent;
    try {
        [bicepContent, bicepparamContent] = await Promise.all([
            readFile(config.bicepPath, 'utf8'),
            readFile(config.bicepparamPath, 'utf8'),
        ]);
    } catch (error) {
        throw new CanvasError(
            'canvas_open_failed',
            `Unable to read Bicep files. ${error instanceof Error ? error.message : String(error)}`
        );
    }

    const parameters = parseBicepparamParameters(bicepparamContent);
    if (preservedValues && typeof preservedValues === 'object') {
        for (const parameter of parameters) {
            if (!Object.hasOwn(preservedValues, parameter.name)) {
                continue;
            }
            parameter.value = coerceParameterValue(parameter, preservedValues[parameter.name]);
        }
    }

    const modules = parseBicepModules(bicepContent);
    const graph = buildArchitectureGraph(modules, parametersToMap(parameters));

    return {
        ...config,
        parameters,
        modules,
        graph,
        updatedAt: new Date().toISOString(),
    };
}

function resolveCanvasInput(input, workspacePath) {
    const rootPath = workspacePath ?? PROJECT_ROOT;
    const candidateRoots = getCandidateRoots(rootPath);
    const requestedBicepPath =
        input && typeof input.bicepPath === 'string' && input.bicepPath.trim().length > 0
            ? input.bicepPath.trim()
            : DEFAULT_BICEP_PATH;
    const requestedBicepparamPath =
        input && typeof input.bicepparamPath === 'string' && input.bicepparamPath.trim().length > 0
            ? input.bicepparamPath.trim()
            : DEFAULT_BICEPPARAM_PATH;

    let resolvedBicepPath = path.resolve(rootPath, requestedBicepPath);
    let resolvedBicepparamPath = path.resolve(rootPath, requestedBicepparamPath);
    let selectedRoot = rootPath;

    if (!path.isAbsolute(requestedBicepPath) && !path.isAbsolute(requestedBicepparamPath)) {
        for (const candidateRoot of candidateRoots) {
            const candidateBicepPath = path.resolve(candidateRoot, requestedBicepPath);
            const candidateBicepparamPath = path.resolve(candidateRoot, requestedBicepparamPath);
            if (existsSync(candidateBicepPath) && existsSync(candidateBicepparamPath)) {
                selectedRoot = candidateRoot;
                resolvedBicepPath = candidateBicepPath;
                resolvedBicepparamPath = candidateBicepparamPath;
                break;
            }
        }
    }

    assertPathInsideRoots(resolvedBicepPath, candidateRoots);
    assertPathInsideRoots(resolvedBicepparamPath, candidateRoots);

    return {
        key: `${resolvedBicepPath}::${resolvedBicepparamPath}`,
        workspacePath: selectedRoot,
        bicepPath: resolvedBicepPath,
        bicepparamPath: resolvedBicepparamPath,
    };
}

async function getOrCreateDocument(config) {
    const existing = documents.get(config.key);
    if (existing) {
        return existing;
    }

    const loaded = await loadDocument(config, undefined);
    documents.set(config.key, loaded);
    return loaded;
}

async function refreshDocument(document, preserveValues) {
    const preserved = preserveValues ? parametersToMap(document.parameters) : undefined;
    const refreshed = await loadDocument(document, preserved);
    documents.set(document.key, refreshed);
    return refreshed;
}

function getInstanceDocument(instanceId) {
    const instance = instances.get(instanceId);
    if (!instance) {
        throw new CanvasError(
            'canvas_instance_not_found',
            `Canvas instance "${instanceId}" is not currently open.`
        );
    }

    const document = documents.get(instance.documentKey);
    if (!document) {
        throw new CanvasError(
            'canvas_state_not_found',
            `No document state found for instance "${instanceId}".`
        );
    }

    return document;
}

function readJsonBody(req) {
    return new Promise((resolve, reject) => {
        const chunks = [];
        req.on('data', (chunk) => chunks.push(chunk));
        req.on('end', () => {
            if (chunks.length === 0) {
                resolve({});
                return;
            }

            try {
                const parsed = JSON.parse(Buffer.concat(chunks).toString('utf8'));
                resolve(parsed);
            } catch {
                reject(new CanvasError('canvas_input_invalid', 'Request body must be valid JSON.'));
            }
        });
        req.on('error', reject);
    });
}

function writeJson(res, statusCode, payload) {
    res.statusCode = statusCode;
    res.setHeader('Content-Type', 'application/json; charset=utf-8');
    res.end(JSON.stringify(payload));
}

function escapeHtml(value) {
    return String(value)
        .replaceAll('&', '&amp;')
        .replaceAll('<', '&lt;')
        .replaceAll('>', '&gt;')
        .replaceAll('"', '&quot;')
        .replaceAll("'", '&#39;');
}

function renderHtml() {
    return `<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>Bicep architecture canvas</title>
    <style>
      :root {
        color-scheme: light dark;
      }

      * {
        box-sizing: border-box;
      }

      body {
        margin: 0;
        background: var(--background-color-default, #ffffff);
        color: var(--text-color-default, #1f2328);
        font-family: var(--font-sans, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif);
        font-size: var(--text-body-medium, 14px);
        line-height: var(--leading-body-medium, 1.5);
      }

      .skip-link {
        position: absolute;
        left: 0;
        top: 0;
        transform: translateY(-140%);
        background: var(--background-color-default, #ffffff);
        color: var(--text-color-default, #1f2328);
        border: 2px solid var(--color-focus-outline, #0969da);
        padding: 0.5rem 0.75rem;
        border-radius: 0.375rem;
        z-index: 999;
      }

      .skip-link:focus {
        transform: translateY(0);
      }

      :focus-visible {
        outline: 2px solid var(--color-focus-outline, #0969da);
        outline-offset: 2px;
      }

      header {
        border-bottom: 1px solid var(--border-color-default, #d0d7de);
        padding: 1rem;
      }

      h1 {
        margin: 0;
        font-size: var(--text-title-large, 1.5rem);
        line-height: var(--leading-title-large, 1.3);
      }

      .layout {
        display: grid;
        grid-template-columns: minmax(260px, 360px) 1fr;
        min-height: calc(100vh - 86px);
      }

      aside {
        border-right: 1px solid var(--border-color-default, #d0d7de);
        padding: 1rem;
        overflow: auto;
      }

      main {
        padding: 1rem;
        overflow: auto;
      }

      .field {
        margin-bottom: 1rem;
      }

      label {
        display: block;
        font-weight: 600;
        margin-bottom: 0.35rem;
      }

      input[type='text'],
      input[type='number'],
      textarea {
        width: 100%;
        border: 1px solid var(--border-color-default, #d0d7de);
        border-radius: 0.375rem;
        padding: 0.4rem 0.5rem;
        background: transparent;
        color: inherit;
        font: inherit;
      }

      textarea {
        min-height: 5rem;
        resize: vertical;
      }

      .checkbox-row {
        display: flex;
        align-items: center;
        gap: 0.5rem;
      }

      .checkbox-row label {
        margin: 0;
        font-weight: 500;
      }

      .actions {
        display: flex;
        flex-wrap: wrap;
        gap: 0.5rem;
        margin: 1rem 0;
      }

      button {
        border: 1px solid var(--border-color-default, #d0d7de);
        border-radius: 0.375rem;
        padding: 0.45rem 0.75rem;
        background: transparent;
        color: inherit;
        font: inherit;
        cursor: pointer;
      }

      button:hover {
        background: color-mix(in srgb, var(--background-color-default, #ffffff) 90%, #0969da 10%);
      }

      .hint {
        color: var(--text-color-muted, #59636e);
        margin: 0.1rem 0 0;
        font-size: 0.9em;
      }

      #status-message {
        min-height: 1.5rem;
        margin-bottom: 0.75rem;
      }

      .sr-only {
        position: absolute;
        width: 1px;
        height: 1px;
        margin: -1px;
        padding: 0;
        overflow: hidden;
        clip: rect(0 0 0 0);
        clip-path: inset(50%);
        border: 0;
        white-space: nowrap;
      }

      .overview {
        margin: 0 0 1rem;
        color: var(--text-color-muted, #59636e);
      }

      .graph-shell {
        border: 1px solid var(--border-color-default, #d0d7de);
        border-radius: 0.5rem;
        min-height: 320px;
        overflow: auto;
      }

      table {
        width: 100%;
        border-collapse: collapse;
        margin-top: 1rem;
      }

      th,
      td {
        border: 1px solid var(--border-color-default, #d0d7de);
        padding: 0.4rem 0.5rem;
        text-align: left;
        vertical-align: top;
      }

      th {
        background: color-mix(in srgb, var(--background-color-default, #ffffff) 92%, #0969da 8%);
      }

      @media (max-width: 960px) {
        .layout {
          grid-template-columns: 1fr;
        }

        aside {
          border-right: 0;
          border-bottom: 1px solid var(--border-color-default, #d0d7de);
        }
      }
    </style>
  </head>
  <body>
    <a href="#main-content" class="skip-link">Skip to architecture canvas</a>
    <header>
      <h1>Bicep architecture canvas</h1>
    </header>
    <div class="layout">
      <aside aria-label="Configuration panel">
        <p id="status-message" role="status" aria-live="polite"></p>
        <form id="parameter-form">
          <div id="parameter-fields"></div>
          <div class="actions">
            <button type="submit">Apply values</button>
            <button type="button" id="refresh-button">Reload files</button>
            <button type="button" id="reset-button">Reset defaults</button>
          </div>
        </form>
      </aside>
      <main id="main-content">
        <h2 id="architecture-heading">Architecture</h2>
        <p class="overview" id="graph-summary"></p>
        <div class="checkbox-row">
          <input id="show-inactive" type="checkbox" checked />
          <label for="show-inactive">Show inactive modules</label>
        </div>
        <div class="graph-shell" id="graph-container" aria-labelledby="architecture-heading"></div>
        <table aria-label="Module status">
          <thead>
            <tr>
              <th scope="col">Module</th>
              <th scope="col">Category</th>
              <th scope="col">Status</th>
              <th scope="col">Condition</th>
            </tr>
          </thead>
          <tbody id="module-table-body"></tbody>
        </table>
      </main>
    </div>
    <script src="/app.js"></script>
  </body>
</html>`;
}

function renderAppJs() {
    return `
const colorByCategory = {
  Core: '#0969da',
  Foundry: '#8250df',
  Data: '#1f883d',
  Search: '#bc4c00',
  Observability: '#0a7ea4',
  Registry: '#953800',
  Hosting: '#9a6700',
  Security: '#cf222e',
};

let state = null;
let showInactive = true;

const parameterForm = document.getElementById('parameter-form');
const parameterFields = document.getElementById('parameter-fields');
const statusMessage = document.getElementById('status-message');
const graphSummary = document.getElementById('graph-summary');
const graphContainer = document.getElementById('graph-container');
const moduleTableBody = document.getElementById('module-table-body');
const showInactiveCheckbox = document.getElementById('show-inactive');
const refreshButton = document.getElementById('refresh-button');
const resetButton = document.getElementById('reset-button');

function setStatus(message, isError = false) {
  statusMessage.textContent = message;
  statusMessage.style.color = isError ? '#cf222e' : '';
}

async function requestJson(url, options = {}) {
  const response = await fetch(url, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  });

  const payload = await response.json();
  if (!response.ok) {
    throw new Error(payload.error || 'Request failed.');
  }

  return payload;
}

function formatValue(parameter) {
  if (parameter.type === 'json') {
    return JSON.stringify(parameter.value, null, 2);
  }
  if (parameter.type === 'bool') {
    return Boolean(parameter.value);
  }
  return parameter.value ?? '';
}

function renderParameterField(parameter) {
  const fieldId = 'param-' + parameter.name;
  const hintId = fieldId + '-hint';
  const hint = parameter.envVar
    ? 'Mapped to environment variable ' + parameter.envVar
    : 'Parameter expression: ' + parameter.expression;

  let controlHtml = '';
  if (parameter.type === 'bool') {
    controlHtml = '<div class="checkbox-row"><input data-param-name="' + parameter.name + '" id="' + fieldId + '" type="checkbox" ' + (parameter.value ? 'checked' : '') + ' /><label for="' + fieldId + '">' + parameter.name + '</label></div>';
    return '<div class="field">' + controlHtml + '<p id="' + hintId + '" class="hint">' + hint + '</p></div>';
  }

  if (parameter.type === 'int') {
    controlHtml = '<label for="' + fieldId + '">' + parameter.name + '</label><input data-param-name="' + parameter.name + '" id="' + fieldId + '" type="number" value="' + String(parameter.value ?? '') + '" aria-describedby="' + hintId + '" />';
  } else if (parameter.type === 'json') {
    controlHtml = '<label for="' + fieldId + '">' + parameter.name + '</label><textarea data-param-name="' + parameter.name + '" id="' + fieldId + '" aria-describedby="' + hintId + '">' + formatValue(parameter) + '</textarea>';
  } else {
    controlHtml = '<label for="' + fieldId + '">' + parameter.name + '</label><input data-param-name="' + parameter.name + '" id="' + fieldId + '" type="text" value="' + String(parameter.value ?? '') + '" aria-describedby="' + hintId + '" />';
  }

  return '<div class="field">' + controlHtml + '<p id="' + hintId + '" class="hint">' + hint + '</p></div>';
}

function computeLevels(nodes, edges) {
  const levels = {};
  for (const node of nodes) {
    levels[node.id] = 0;
  }

  let changed = true;
  let guard = 0;
  while (changed && guard < 400) {
    changed = false;
    guard += 1;
    for (const edge of edges) {
      const nextLevel = (levels[edge.from] ?? 0) + 1;
      if ((levels[edge.to] ?? 0) < nextLevel) {
        levels[edge.to] = nextLevel;
        changed = true;
      }
    }
  }

  return levels;
}

function createSvgNode(svg, namespace, node, x, y) {
  const width = 210;
  const height = 82;
  const border = node.active ? '#1f2328' : '#8c959f';
  const fill = node.active ? (colorByCategory[node.category] || '#57606a') : '#d8dee4';
  const textColor = node.active ? '#ffffff' : '#1f2328';

  const group = document.createElementNS(namespace, 'g');

  const rect = document.createElementNS(namespace, 'rect');
  rect.setAttribute('x', String(x));
  rect.setAttribute('y', String(y));
  rect.setAttribute('rx', '8');
  rect.setAttribute('ry', '8');
  rect.setAttribute('width', String(width));
  rect.setAttribute('height', String(height));
  rect.setAttribute('fill', fill);
  rect.setAttribute('stroke', border);
  rect.setAttribute('stroke-width', '1.4');
  group.appendChild(rect);

  const title = document.createElementNS(namespace, 'text');
  title.setAttribute('x', String(x + 10));
  title.setAttribute('y', String(y + 24));
  title.setAttribute('font-size', '13');
  title.setAttribute('font-weight', '700');
  title.setAttribute('fill', textColor);
  title.textContent = node.label;
  group.appendChild(title);

  const subtitle = document.createElementNS(namespace, 'text');
  subtitle.setAttribute('x', String(x + 10));
  subtitle.setAttribute('y', String(y + 44));
  subtitle.setAttribute('font-size', '11');
  subtitle.setAttribute('fill', textColor);
  subtitle.textContent = node.category + (node.active ? '' : ' (inactive)');
  group.appendChild(subtitle);

  if (node.condition) {
    const conditionText = document.createElementNS(namespace, 'text');
    conditionText.setAttribute('x', String(x + 10));
    conditionText.setAttribute('y', String(y + 64));
    conditionText.setAttribute('font-size', '10');
    conditionText.setAttribute('fill', textColor);
    conditionText.textContent = node.condition;
    group.appendChild(conditionText);
  }

  svg.appendChild(group);
}

function renderGraph() {
  graphContainer.replaceChildren();
  if (!state) {
    return;
  }

  const sourceNodes = showInactive
    ? state.graph.nodes
    : state.graph.nodes.filter((node) => node.active);

  if (sourceNodes.length === 0) {
    graphContainer.textContent = 'No modules available for the current filter.';
    return;
  }

  const visibleNodeIds = new Set(sourceNodes.map((node) => node.id));
  const visibleEdges = state.graph.edges.filter(
    (edge) => visibleNodeIds.has(edge.from) && visibleNodeIds.has(edge.to)
  );

  const namespace = 'http://www.w3.org/2000/svg';
  const svg = document.createElementNS(namespace, 'svg');
  svg.setAttribute('role', 'img');
  svg.setAttribute('aria-label', 'Architecture graph generated from Bicep modules');

  const levels = computeLevels(sourceNodes, visibleEdges);
  const buckets = {};
  for (const node of sourceNodes) {
    const level = levels[node.id] ?? 0;
    if (!buckets[level]) {
      buckets[level] = [];
    }
    buckets[level].push(node);
  }

  for (const key of Object.keys(buckets)) {
    buckets[key].sort((a, b) => {
      if (a.active !== b.active) {
        return a.active ? -1 : 1;
      }
      return a.label.localeCompare(b.label);
    });
  }

  const levelValues = Object.keys(buckets).map((value) => Number(value));
  const maxLevel = Math.max(...levelValues);
  let maxRows = 0;
  for (const level of levelValues) {
    maxRows = Math.max(maxRows, buckets[level].length);
  }

  const width = Math.max(860, (maxLevel + 1) * 250 + 120);
  const height = Math.max(360, maxRows * 110 + 90);
  svg.setAttribute('viewBox', '0 0 ' + width + ' ' + height);
  svg.setAttribute('width', String(width));
  svg.setAttribute('height', String(height));

  const defs = document.createElementNS(namespace, 'defs');
  const marker = document.createElementNS(namespace, 'marker');
  marker.setAttribute('id', 'arrow');
  marker.setAttribute('markerWidth', '8');
  marker.setAttribute('markerHeight', '8');
  marker.setAttribute('refX', '7');
  marker.setAttribute('refY', '4');
  marker.setAttribute('orient', 'auto');
  const path = document.createElementNS(namespace, 'path');
  path.setAttribute('d', 'M 0 0 L 8 4 L 0 8 z');
  path.setAttribute('fill', '#57606a');
  marker.appendChild(path);
  defs.appendChild(marker);
  svg.appendChild(defs);

  const positions = {};
  for (const level of levelValues) {
    const nodes = buckets[level];
    for (let index = 0; index < nodes.length; index += 1) {
      const x = 40 + level * 250;
      const y = 30 + index * 106;
      positions[nodes[index].id] = { x, y };
    }
  }

  for (const edge of visibleEdges) {
    const from = positions[edge.from];
    const to = positions[edge.to];
    if (!from || !to) {
      continue;
    }

    const line = document.createElementNS(namespace, 'line');
    line.setAttribute('x1', String(from.x + 210));
    line.setAttribute('y1', String(from.y + 40));
    line.setAttribute('x2', String(to.x));
    line.setAttribute('y2', String(to.y + 40));
    line.setAttribute('stroke', '#57606a');
    line.setAttribute('stroke-width', '1.2');
    line.setAttribute('marker-end', 'url(#arrow)');
    svg.appendChild(line);
  }

  for (const node of sourceNodes) {
    const position = positions[node.id];
    createSvgNode(svg, namespace, node, position.x, position.y);
  }

  graphContainer.appendChild(svg);
}

function renderModulesTable() {
  moduleTableBody.replaceChildren();
  if (!state) {
    return;
  }

  const rows = showInactive
    ? state.graph.nodes
    : state.graph.nodes.filter((node) => node.active);

  for (const node of rows) {
    const row = document.createElement('tr');
    row.innerHTML =
      '<th scope="row">' + node.label + '</th>' +
      '<td>' + node.category + '</td>' +
      '<td>' + (node.active ? 'Active' : 'Inactive') + '</td>' +
      '<td>' + (node.condition || 'Always') + '</td>';
    moduleTableBody.appendChild(row);
  }
}

function renderAll() {
  if (!state) {
    return;
  }

  parameterFields.innerHTML = state.parameters.map(renderParameterField).join('');
  graphSummary.textContent =
    state.graph.activeCount +
    ' active modules, ' +
    state.graph.inactiveCount +
    ' inactive modules. ' +
    state.files.bicepparamPath;
  renderGraph();
  renderModulesTable();
}

function collectParameterUpdates() {
  const updates = {};
  for (const parameter of state.parameters) {
    const selector = '[data-param-name="' + parameter.name + '"]';
    const field = parameterFields.querySelector(selector);
    if (!field) {
      continue;
    }

    if (parameter.type === 'bool') {
      updates[parameter.name] = Boolean(field.checked);
      continue;
    }

    if (parameter.type === 'int') {
      const parsed = Number.parseInt(field.value, 10);
      if (Number.isNaN(parsed)) {
        throw new Error('Parameter "' + parameter.name + '" must be an integer.');
      }
      updates[parameter.name] = parsed;
      continue;
    }

    if (parameter.type === 'json') {
      if (!field.value.trim()) {
        updates[parameter.name] = null;
      } else {
        updates[parameter.name] = JSON.parse(field.value);
      }
      continue;
    }

    updates[parameter.name] = field.value;
  }

  return updates;
}

parameterForm.addEventListener('submit', async (event) => {
  event.preventDefault();
  try {
    const values = collectParameterUpdates();
    state = await requestJson('/api/parameters', {
      method: 'POST',
      body: JSON.stringify({ values }),
    });
    renderAll();
    setStatus('Parameter values applied.');
  } catch (error) {
    setStatus(error.message, true);
  }
});

refreshButton.addEventListener('click', async () => {
  try {
    state = await requestJson('/api/refresh', {
      method: 'POST',
      body: JSON.stringify({}),
    });
    renderAll();
    setStatus('Reloaded Bicep files while keeping current overrides.');
  } catch (error) {
    setStatus(error.message, true);
  }
});

resetButton.addEventListener('click', async () => {
  try {
    state = await requestJson('/api/reset', {
      method: 'POST',
      body: JSON.stringify({}),
    });
    renderAll();
    setStatus('Reset to defaults from main.bicepparam.');
  } catch (error) {
    setStatus(error.message, true);
  }
});

showInactiveCheckbox.addEventListener('change', () => {
  showInactive = Boolean(showInactiveCheckbox.checked);
  renderGraph();
  renderModulesTable();
});

async function initialize() {
  try {
    state = await requestJson('/api/state');
    renderAll();
    setStatus('Loaded architecture from Bicep files.');
  } catch (error) {
    setStatus(error.message, true);
  }
}

initialize();
`;
}

async function handleHttpRequest(req, res, instanceId) {
    const instance = instances.get(instanceId);
    if (!instance) {
        writeJson(res, 404, { error: 'Canvas instance was not found.' });
        return;
    }

    const document = documents.get(instance.documentKey);
    if (!document) {
        writeJson(res, 404, { error: 'Canvas document state was not found.' });
        return;
    }

    const requestUrl = new URL(req.url ?? '/', 'http://127.0.0.1');
    const pathname = requestUrl.pathname;

    if (req.method === 'GET' && pathname === '/') {
        res.statusCode = 200;
        res.setHeader('Content-Type', 'text/html; charset=utf-8');
        res.end(renderHtml());
        return;
    }

    if (req.method === 'GET' && pathname === '/app.js') {
        res.statusCode = 200;
        res.setHeader('Content-Type', 'application/javascript; charset=utf-8');
        res.end(renderAppJs());
        return;
    }

    if (req.method === 'GET' && pathname === '/api/state') {
        writeJson(res, 200, createDocumentResponse(document));
        return;
    }

    if (req.method === 'POST' && pathname === '/api/parameters') {
        const body = await readJsonBody(req);
        if (!body || typeof body !== 'object' || Array.isArray(body)) {
            throw new CanvasError('canvas_input_invalid', 'Request payload must be an object.');
        }
        if (!Object.hasOwn(body, 'values') || typeof body.values !== 'object' || body.values === null) {
            throw new CanvasError(
                'canvas_input_invalid',
                'Request payload must include a "values" object.'
            );
        }

        applyParameterValues(document, body.values);
        document.updatedAt = new Date().toISOString();
        writeJson(res, 200, createDocumentResponse(document));
        return;
    }

    if (req.method === 'POST' && pathname === '/api/refresh') {
        const refreshed = await refreshDocument(document, true);
        writeJson(res, 200, createDocumentResponse(refreshed));
        return;
    }

    if (req.method === 'POST' && pathname === '/api/reset') {
        resetParameterValues(document);
        document.updatedAt = new Date().toISOString();
        writeJson(res, 200, createDocumentResponse(document));
        return;
    }

    writeJson(res, 404, { error: `No route found for ${escapeHtml(pathname)}.` });
}

async function startServer(instanceId) {
    const server = createServer((req, res) => {
        void handleHttpRequest(req, res, instanceId).catch((error) => {
            const message =
                error instanceof CanvasError
                    ? error.message
                    : error instanceof Error
                      ? error.message
                      : String(error);
            writeJson(res, 400, { error: message });
        });
    });

    await new Promise((resolve) => server.listen(0, '127.0.0.1', resolve));
    const address = server.address();
    const port = typeof address === 'object' && address ? address.port : 0;
    return {
        server,
        url: `http://127.0.0.1:${port}/`,
    };
}

const session = await joinSession({
    canvases: [
        createCanvas({
            id: 'azure-bicep-architecture',
            displayName: 'Azure Bicep architecture',
            description:
                'Visualizes infra Bicep modules and lets you configure main.bicepparam values to see architecture changes.',
            inputSchema: {
                type: 'object',
                additionalProperties: false,
                properties: {
                    bicepPath: {
                        type: 'string',
                        description: 'Path to a Bicep file relative to workspace root.',
                    },
                    bicepparamPath: {
                        type: 'string',
                        description: 'Path to a .bicepparam file relative to workspace root.',
                    },
                },
            },
            actions: [
                {
                    name: 'get_state',
                    description: 'Return the current canvas state, including parameters and graph.',
                    handler: async (ctx) => {
                        const document = getInstanceDocument(ctx.instanceId);
                        return createDocumentResponse(document);
                    },
                },
                {
                    name: 'set_parameter_values',
                    description: 'Apply parameter updates and return the refreshed graph.',
                    inputSchema: {
                        type: 'object',
                        additionalProperties: false,
                        required: ['values'],
                        properties: {
                            values: {
                                type: 'object',
                                description: 'Map of parameter names to updated values.',
                            },
                        },
                    },
                    handler: async (ctx) => {
                        const document = getInstanceDocument(ctx.instanceId);
                        if (!ctx.input || typeof ctx.input !== 'object' || Array.isArray(ctx.input)) {
                            throw new CanvasError('canvas_input_invalid', 'Action input must be an object.');
                        }

                        const values = ctx.input.values;
                        if (!values || typeof values !== 'object' || Array.isArray(values)) {
                            throw new CanvasError(
                                'canvas_input_invalid',
                                'Action input must include a "values" object.'
                            );
                        }

                        applyParameterValues(document, values);
                        document.updatedAt = new Date().toISOString();
                        return createDocumentResponse(document);
                    },
                },
                {
                    name: 'refresh_from_files',
                    description: 'Re-parse Bicep and bicepparam files while preserving current values.',
                    handler: async (ctx) => {
                        const document = getInstanceDocument(ctx.instanceId);
                        const refreshed = await refreshDocument(document, true);
                        return createDocumentResponse(refreshed);
                    },
                },
                {
                    name: 'reset_to_defaults',
                    description: 'Reset all parameters to defaults from the bicepparam file.',
                    handler: async (ctx) => {
                        const document = getInstanceDocument(ctx.instanceId);
                        resetParameterValues(document);
                        document.updatedAt = new Date().toISOString();
                        return createDocumentResponse(document);
                    },
                },
            ],
            open: async (ctx) => {
                const config = resolveCanvasInput(ctx.input, session.workspacePath);
                const document = await getOrCreateDocument(config);

                let instance = instances.get(ctx.instanceId);
                if (!instance) {
                    const started = await startServer(ctx.instanceId);
                    instance = {
                        ...started,
                        documentKey: document.key,
                    };
                    instances.set(ctx.instanceId, instance);
                } else if (instance.documentKey !== document.key) {
                    await new Promise((resolve) => instance.server.close(() => resolve()));
                    const started = await startServer(ctx.instanceId);
                    instance = {
                        ...started,
                        documentKey: document.key,
                    };
                    instances.set(ctx.instanceId, instance);
                }

                return {
                    title: 'Azure architecture from Bicep',
                    status: `${document.graph.activeCount} active modules`,
                    url: instance.url,
                };
            },
            onClose: async (ctx) => {
                const instance = instances.get(ctx.instanceId);
                if (!instance) {
                    return;
                }

                instances.delete(ctx.instanceId);
                await new Promise((resolve) => instance.server.close(() => resolve()));
            },
        }),
    ],
});

await session.log('Loaded canvas extension "azure-bicep-architecture".', {
    level: 'info',
    ephemeral: true,
});

/**
 * @typedef {Object} CanvasParameter
 * @property {string} name
 * @property {'string' | 'int' | 'bool' | 'json'} type
 * @property {string | null} envVar
 * @property {string} expression
 * @property {unknown} defaultValue
 * @property {unknown} value
 */

/**
 * @typedef {Object} CanvasModule
 * @property {string} id
 * @property {string} name
 * @property {string} title
 * @property {string} path
 * @property {string} category
 * @property {string | null} condition
 * @property {string[]} rawDependsOn
 * @property {string[]} dependsOn
 */

/**
 * @typedef {Object} CanvasDocument
 * @property {string} key
 * @property {string} workspacePath
 * @property {string} bicepPath
 * @property {string} bicepparamPath
 * @property {CanvasParameter[]} parameters
 * @property {CanvasModule[]} modules
 * @property {{nodes: Array<Record<string, unknown>>, edges: Array<Record<string, string>>, activeCount: number, inactiveCount: number}} graph
 * @property {string} updatedAt
 */
