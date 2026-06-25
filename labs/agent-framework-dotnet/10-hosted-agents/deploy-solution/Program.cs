using Azure.AI.Projects.Agents;
using Azure.Identity;
using DotNetEnv;
using System.ClientModel.Primitives;

#pragma warning disable AAIP001 // Hosted agents are an experimental preview feature.

// Load environment variables from .env in the repository root (searches parent directories)
Env.TraversePath().Load();

var endpoint = Environment.GetEnvironmentVariable("FOUNDRY_PROJECT_ENDPOINT")
    ?? throw new InvalidOperationException(
        "FOUNDRY_PROJECT_ENDPOINT is not set. Copy shared/.env.example to .env in the repository root and fill in your values.");

var agentName = Environment.GetEnvironmentVariable("HOSTED_AGENT_NAME") ?? "trip-disruption-concierge";

// ── Create the administration client ──────────────────────────────────────────
// AgentAdministrationClient manages the lifecycle of hosted agents: create,
// update, poll, download, and delete versions.
// FeaturePolicy injects the required Foundry-Features preview header.
var options = new AgentAdministrationClientOptions();
options.AddPolicy(
    new FeaturePolicy("HostedAgents=V1Preview,CodeAgents=V1Preview"),
    PipelinePosition.PerCall);

var agentsClient = new AgentAdministrationClient(
    endpoint: new Uri(endpoint),
    tokenProvider: new DefaultAzureCredential(),
    options: options);

// ── Define and deploy from source ─────────────────────────────────────────────
// remote_build mode: Foundry runs `dotnet restore` and `dotnet publish` for you
// during provisioning - no local Docker build required.
// entryPoint refers to the DLL name produced by the server-side `dotnet publish`.
// filePath must be run from the repository root so the relative path resolves.
var agentDefinition = new HostedAgentDefinition(cpu: "1", memory: "2Gi")
{
    Versions = { new ProtocolVersionRecord(ProjectsAgentProtocol.Responses, "1.0.0") },
    CodeConfiguration = new CodeConfiguration(
        runtime: "dotnet_10",
        entryPoint: ["dotnet", "TripConcierge.HostedAgent.dll"],
        dependencyResolution: CodeDependencyResolution.RemoteBuild),
};

var metadata = new CreateAgentVersionFromCodeMetadata(agentDefinition);

Console.WriteLine($"Deploying {agentName} from source code ...");
ProjectsAgentVersion agentVersion = agentsClient.CreateAgentVersionFromCode(
    agentName: agentName,
    filePath: "./labs/agent-framework-dotnet/10-hosted-agents/solution",
    metadata: metadata);
Console.WriteLine($"Created version: {agentVersion.Version}  status: {agentVersion.Status}");

// ── Poll for active ───────────────────────────────────────────────────────────
while (agentVersion.Status != AgentVersionStatus.Active &&
       agentVersion.Status != AgentVersionStatus.Failed)
{
    Thread.Sleep(5_000);
    agentVersion = agentsClient.GetAgentVersion(
        agentName: agentVersion.Name,
        agentVersion: agentVersion.Version);
    Console.WriteLine($"  Status: {agentVersion.Status}");
}

if (agentVersion.Status != AgentVersionStatus.Active)
    throw new InvalidOperationException($"Deployment failed - status: {agentVersion.Status}");

Console.WriteLine($"Agent {agentName} v{agentVersion.Version} is active and ready.");

// ── FeaturePolicy ─────────────────────────────────────────────────────────────
// Injects the Foundry-Features preview header required by the hosted-agents API.
// Required while source-code deployment is in preview.
internal class FeaturePolicy(string feature) : PipelinePolicy
{
    private const string FeatureHeader = "Foundry-Features";

    public override void Process(
        PipelineMessage message,
        IReadOnlyList<PipelinePolicy> pipeline,
        int currentIndex)
    {
        message.Request.Headers.Add(FeatureHeader, feature);
        ProcessNext(message, pipeline, currentIndex);
    }

    public override async ValueTask ProcessAsync(
        PipelineMessage message,
        IReadOnlyList<PipelinePolicy> pipeline,
        int currentIndex)
    {
        message.Request.Headers.Add(FeatureHeader, feature);
        await ProcessNextAsync(message, pipeline, currentIndex);
    }
}
