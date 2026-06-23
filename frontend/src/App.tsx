import { useEffect, useRef, useState } from "react";
import {
  Alert,
  Box,
  Button,
  Container,
  Heading,
  HStack,
  Input,
  Stack,
  Text,
} from "@chakra-ui/react";
import { fetchBeers, uploadBeerPhoto, type Beer } from "./api";

export default function App() {
  const [beers, setBeers] = useState<Beer[]>([]);
  const [token, setToken] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const fileRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    fetchBeers()
      .then(setBeers)
      .catch((caught: Error) => setError(caught.message));
  }, []);

  async function handleUpload() {
    const file = fileRef.current?.files?.[0];
    if (!file) {
      setError("Choose a photo first");
      return;
    }
    setBusy(true);
    setError(null);
    try {
      setBeers(await uploadBeerPhoto(file, token));
    } catch (caught) {
      setError((caught as Error).message);
    } finally {
      setBusy(false);
    }
  }

  return (
    <Container maxW="2xl" py="8">
      <Heading mb="6">Shoes &amp; Brews</Heading>

      {error && (
        <Alert.Root status="error" mb="4">
          <Alert.Indicator />
          <Alert.Title>{error}</Alert.Title>
        </Alert.Root>
      )}

      <Stack gap="4" mb="8">
        {beers.length === 0 && (
          <Text color="fg.muted">No beers on the list yet.</Text>
        )}
        {beers.map((beer, index) => (
          <Box key={index} borderWidth="1px" borderRadius="md" p="4">
            <Text fontWeight="bold">{beer.name}</Text>
            <Text color="fg.muted">
              {[
                beer.brewery,
                beer.style,
                beer.abv ? `${beer.abv}%` : null,
                beer.price,
              ]
                .filter(Boolean)
                .join(" · ")}
            </Text>
          </Box>
        ))}
      </Stack>

      <Heading size="md" mb="3">
        Update the list
      </Heading>
      <Stack gap="3">
        <Input type="file" accept="image/*" ref={fileRef} p="1" />
        <Input
          type="password"
          placeholder="Upload token"
          value={token}
          onChange={(event) => setToken(event.target.value)}
        />
        <HStack>
          <Button onClick={handleUpload} loading={busy} disabled={!token}>
            Upload photo
          </Button>
        </HStack>
      </Stack>
    </Container>
  );
}
