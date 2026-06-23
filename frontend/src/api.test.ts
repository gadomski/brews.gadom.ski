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

  it("uploadBeerPhoto requests a URL, PUTs to S3, then processes", async () => {
    const fetchMock = vi
      .fn()
      .mockResolvedValueOnce(
        new Response(
          JSON.stringify({
            url: "https://s3.example.com/up",
            key: "uploads/abc",
          }),
          { status: 200 },
        ),
      )
      .mockResolvedValueOnce(new Response(null, { status: 200 }))
      .mockResolvedValueOnce(
        new Response(JSON.stringify([{ name: "Pils" }]), { status: 200 }),
      );
    vi.stubGlobal("fetch", fetchMock);
    const file = new File(["test"], "test.jpg", { type: "image/jpeg" });

    const beers = await uploadBeerPhoto(file, "test-token");

    expect(beers).toEqual([{ name: "Pils" }]);
    expect(fetchMock.mock.calls[0][0]).toBe("/api/beers/upload-url");
    expect(fetchMock.mock.calls[0][1]?.method).toBe("POST");
    expect(fetchMock.mock.calls[1][0]).toBe("https://s3.example.com/up");
    expect(fetchMock.mock.calls[1][1]?.method).toBe("PUT");
    expect(fetchMock.mock.calls[2][0]).toBe("/api/beers/process");
    expect(JSON.parse(fetchMock.mock.calls[2][1]?.body as string)).toEqual({
      key: "uploads/abc",
    });
  });

  it("uploadBeerPhoto throws when the S3 PUT fails", async () => {
    const fetchMock = vi
      .fn()
      .mockResolvedValueOnce(
        new Response(
          JSON.stringify({
            url: "https://s3.example.com/up",
            key: "uploads/abc",
          }),
          { status: 200 },
        ),
      )
      .mockResolvedValueOnce(new Response(null, { status: 403 }));
    vi.stubGlobal("fetch", fetchMock);
    const file = new File(["test"], "test.jpg", { type: "image/jpeg" });

    await expect(uploadBeerPhoto(file, "test-token")).rejects.toThrow();
    expect(fetchMock).toHaveBeenCalledTimes(2);
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
