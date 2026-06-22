export interface Beer {
  name: string
  brewery: string | null
  style: string | null
  abv: number | null
  price: string | null
}

export async function fetchBeers(): Promise<Beer[]> {
  const response = await fetch("/api/beers")
  if (!response.ok) {
    throw new Error("Failed to load the beer list")
  }
  return response.json()
}

export async function uploadBeerPhoto(file: File, token: string): Promise<Beer[]> {
  const body = new FormData()
  body.append("file", file)
  const response = await fetch("/api/beers/upload", {
    method: "POST",
    headers: { "X-Upload-Token": token },
    body,
  })
  if (!response.ok) {
    throw new Error(`Upload failed (${response.status})`)
  }
  return response.json()
}
