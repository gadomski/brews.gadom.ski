export interface Beer {
  name: string
  brewery: string | null
  style: string | null
  abv: number | null
  price: string | null
}

function apiUrl(path: string): string {
  const base = (import.meta.env.VITE_API_BASE_URL ?? "").replace(/\/$/, "")
  return `${base}${path}`
}

export async function fetchBeers(): Promise<Beer[]> {
  const response = await fetch(apiUrl("/api/beers"))
  if (!response.ok) {
    throw new Error("Failed to load the beer list")
  }
  return response.json()
}

export async function uploadBeerPhoto(file: File, token: string): Promise<Beer[]> {
  const body = new FormData()
  body.append("file", file)
  const response = await fetch(apiUrl("/api/beers/upload"), {
    method: "POST",
    headers: { "X-Upload-Token": token },
    body,
  })
  if (!response.ok) {
    throw new Error(`Upload failed (${response.status})`)
  }
  return response.json()
}
