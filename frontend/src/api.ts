export interface Beer {
  name: string;
  brewery: string | null;
  style: string | null;
  abv: number | null;
  price: string | null;
}

function apiUrl(path: string): string {
  const base = (import.meta.env.VITE_API_BASE_URL ?? "").replace(/\/$/, "");
  return `${base}${path}`;
}

export async function fetchBeers(): Promise<Beer[]> {
  const response = await fetch(apiUrl("/api/beers"));
  if (!response.ok) {
    throw new Error("Failed to load the beer list");
  }
  return response.json();
}

export async function uploadBeerPhoto(
  file: File,
  token: string,
): Promise<Beer[]> {
  const urlResponse = await fetch(apiUrl("/api/beers/upload-url"), {
    method: "POST",
    headers: { "X-Upload-Token": token, "Content-Type": "application/json" },
    body: JSON.stringify({ content_type: file.type }),
  });
  if (!urlResponse.ok) {
    throw new Error(`Could not start upload (${urlResponse.status})`);
  }
  const { url, key } = (await urlResponse.json()) as {
    url: string;
    key: string;
  };

  const putResponse = await fetch(url, {
    method: "PUT",
    headers: { "Content-Type": file.type },
    body: file,
  });
  if (!putResponse.ok) {
    throw new Error(`Upload failed (${putResponse.status})`);
  }

  const processResponse = await fetch(apiUrl("/api/beers/process"), {
    method: "POST",
    headers: { "X-Upload-Token": token, "Content-Type": "application/json" },
    body: JSON.stringify({ key }),
  });
  if (!processResponse.ok) {
    throw new Error(`Processing failed (${processResponse.status})`);
  }
  return processResponse.json();
}
