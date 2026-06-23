import { describe, it, expect, afterEach, vi } from "vitest";
import { fetchBeers, uploadBeerPhoto } from "./api";

describe("api", () => {
  afterEach(() => {
    vi.restoreAllMocks();
    vi.unstubAllEnvs();
  });

  it("fetchBeers calls /api/beers", async () => {
    const fetchMock = vi.fn(
      async () => new Response(JSON.stringify([]), { status: 200 }),
    );
    vi.stubGlobal("fetch", fetchMock);
    await fetchBeers();
    expect(fetchMock).toHaveBeenCalledWith("/api/beers");
  });

  it("uploadBeerPhoto calls /api/beers/upload with POST", async () => {
    const fetchMock = vi.fn(
      async () => new Response(JSON.stringify([]), { status: 200 }),
    );
    vi.stubGlobal("fetch", fetchMock);
    const file = new File(["test"], "test.jpg", { type: "image/jpeg" });
    await uploadBeerPhoto(file, "test-token");
    expect(fetchMock).toHaveBeenCalledWith(
      "/api/beers/upload",
      expect.any(Object),
    );
    const call = fetchMock.mock.calls[0];
    expect(call[1]?.method).toBe("POST");
    expect(call[1]?.headers).toEqual({ "X-Upload-Token": "test-token" });
  });

  it("fetchBeers throws error on non-ok response", async () => {
    const fetchMock = vi.fn(
      async () => new Response(JSON.stringify({}), { status: 500 }),
    );
    vi.stubGlobal("fetch", fetchMock);
    await expect(fetchBeers()).rejects.toThrow();
  });

  it("requests are prefixed with VITE_API_BASE_URL", async () => {
    vi.stubEnv("VITE_API_BASE_URL", "https://api.example.com/");
    const fetchMock = vi.fn(
      async () => new Response(JSON.stringify([]), { status: 200 }),
    );
    vi.stubGlobal("fetch", fetchMock);
    await fetchBeers();
    expect(fetchMock.mock.calls[0][0]).toBe(
      "https://api.example.com/api/beers",
    );
  });
});
