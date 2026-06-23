import { useEffect, useRef, useState } from "react";
import {
  Alert,
  Box,
  Button,
  Center,
  Container,
  Heading,
  HStack,
  Input,
  SimpleGrid,
  Stack,
  Text,
} from "@chakra-ui/react";
import { fetchBeers, uploadBeerPhoto, type Beer } from "./api";
import { BrewsIcon } from "./BrewsIcon";

const CHALK = "#f3eede";
const CHALK_MUTED = "#b9c6bd";

const chalkboard = {
  bg: "#14181a",
  color: CHALK,
  borderRadius: "lg",
  borderWidth: "2px",
  borderColor: "#000000",
  shadow: "lg",
};

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
    <Container py="6">
      <Stack gap={6}>
        <Center>
          <HStack gap="3">
            <BrewsIcon boxSize="14" />
            <Heading
              fontSize="6xl"
              fontWeight="700"
              lineHeight="1"
              color={CHALK}
              textShadow="0 1px 3px rgba(0,0,0,0.45)"
            >
              Shoes &amp; Brews
            </Heading>
          </HStack>
        </Center>

        <SimpleGrid columns={{ base: 1, md: 4 }} gap={2}>
          {beers.length === 0 && (
            <Text color={CHALK} textShadow="0 1px 2px rgba(0,0,0,0.45)">
              No beers on the list yet.
            </Text>
          )}
          {beers.map((beer, index) => (
            <Box key={index} {...chalkboard} fontFamily="heading" p="4">
              <Text fontWeight="bold" fontSize="2xl" lineHeight="1.1">
                {beer.name}
              </Text>
              <Text color={CHALK_MUTED} fontSize="lg" lineHeight="1.2">
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
        </SimpleGrid>

        {error && (
          <Alert.Root status="error" mb="4">
            <Alert.Indicator />
            <Alert.Title>{error}</Alert.Title>
          </Alert.Root>
        )}

        <Box {...chalkboard} p="5">
          <Heading fontSize="3xl" fontWeight="700" mb="2" color={CHALK}>
            Update the list
          </Heading>
          <Stack gap="3">
            <Input
              type="file"
              accept="image/*"
              ref={fileRef}
              p="1"
              bg="bg.panel"
              color="fg"
            />
            <Input
              type="password"
              placeholder="Upload token"
              value={token}
              onChange={(event) => setToken(event.target.value)}
              bg="bg.panel"
              color="fg"
            />
            <HStack>
              <Button onClick={handleUpload} loading={busy} disabled={!token}>
                Upload photo
              </Button>
            </HStack>
          </Stack>
        </Box>
      </Stack>
    </Container>
  );
}
