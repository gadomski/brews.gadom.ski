import { Container, Skeleton, Stack } from "@chakra-ui/react";

import Beers from "./components/Beers";
import Header from "./components/Header";
import useBeers from "./hooks/useBeers";

export default function App() {
  const result = useBeers();

  return (
    <Container py={4}>
      <Stack gap={4}>
        <Header />
        {(result.isLoading && <Skeleton />) ||
          (result.data && <Beers beers={result.data} />)}
      </Stack>
    </Container>
  );
}
