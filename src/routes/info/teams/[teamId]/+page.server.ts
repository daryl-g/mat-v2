const BASE_URL =
  "https://raw.githubusercontent.com/daryl-g/mat-v2/refs/heads/svelte-version/data/opta/2026 ASEAN Championship";

export async function load({ params }) {
  const [teamsResponse, squadsResponse] = await Promise.all([
    fetch(`${BASE_URL}/teams.json`),
    fetch(`${BASE_URL}/squads.json`),
  ]);

  const { teams } = await teamsResponse.json();
  const { squads } = await squadsResponse.json();

  // Find the team for the current teamId and merge in the squad details
  const teamId = params.teamId;
  const team = teams.find((t: Record<string, any>) => t.id === teamId);
  const squad = squads.find((s: Record<string, any>) => s.teamId === teamId);

  if (!team) {
    throw new Error("Team not found");
  }

  return { team: { ...team, squad } };
}
