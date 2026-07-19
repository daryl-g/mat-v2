const BASE_URL =
  "https://raw.githubusercontent.com/daryl-g/mat-v2/refs/heads/svelte-version/data/opta/2026 ASEAN Championship";

export async function load() {
  const teamsResponse = await fetch(`${BASE_URL}/teams.json`);
  const teams = await teamsResponse.json();
  return teams;
}
