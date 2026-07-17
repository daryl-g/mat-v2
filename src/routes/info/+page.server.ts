// Default redirect to the groups page
import { redirect } from "@sveltejs/kit";

export function load() {
  redirect(302, "/info/groups");
}
