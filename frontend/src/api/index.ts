import { client } from "./client";
import type { components } from "./schema";

export type Beer = components["schemas"]["Beer"];

export async function fetchBeers(): Promise<Beer[]> {
  const { data, error } = await client.GET("/beers");
  if (error) {
    throw new Error("Failed to load the beer list");
  }
  return data;
}
