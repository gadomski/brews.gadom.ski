import { afterEach, expect, test, vi } from "vitest"
import { fetchBeers, uploadBeerPhoto } from "./api"

afterEach(() => {
  vi.restoreAllMocks()
})

test("fetchBeers returns the parsed list", async () => {
  vi.stubGlobal(
    "fetch",
    vi.fn(async () => new Response(JSON.stringify([{ name: "Pils" }]), { status: 200 })),
  )
  const beers = await fetchBeers()
  expect(beers).toEqual([{ name: "Pils" }])
})

test("uploadBeerPhoto sends the token header", async () => {
  const fetchMock = vi.fn(async () => new Response(JSON.stringify([]), { status: 200 }))
  vi.stubGlobal("fetch", fetchMock)
  await uploadBeerPhoto(new File(["x"], "list.jpg", { type: "image/jpeg" }), "secret")
  const [, options] = fetchMock.mock.calls[0]
  expect((options.headers as Record<string, string>)["X-Upload-Token"]).toBe("secret")
})

test("uploadBeerPhoto throws on a non-OK response", async () => {
  vi.stubGlobal("fetch", vi.fn(async () => new Response("nope", { status: 401 })))
  await expect(
    uploadBeerPhoto(new File(["x"], "list.jpg", { type: "image/jpeg" }), "wrong"),
  ).rejects.toThrow()
})
