import {
  Box,
  Flex,
  Heading,
  Separator,
  SimpleGrid,
  Stack,
  Text,
} from "@chakra-ui/react";

import type { Beer } from "../api";
import { CHALK_MUTED, CHALKBOARD } from "../constants";

export default function Beers({ beers }: { beers: Beer[] }) {
  return (
    <SimpleGrid columns={{ base: 1, md: 4 }} gap={2}>
      {beers.map((beer, index) => (
        <Beer key={index} beer={beer} />
      ))}
    </SimpleGrid>
  );
}

function Beer({ beer }: { beer: Beer }) {
  const prices = beer.price?.split("/").map((price) => price.trim()) ?? [];
  return (
    <Box {...CHALKBOARD} fontFamily={"heading"} px={3} py={4}>
      <Flex justify={"space-between"} gap={3}>
        <Box>
          <Heading fontSize={"x-large"}>{beer.name}</Heading>
          <Text color={CHALK_MUTED} fontSize={"lg"}>
            {[beer.brewery, beer.style, beer.abv ? `${beer.abv}%` : null]
              .filter(Boolean)
              .join(" · ")}
          </Text>
        </Box>
        {prices.length > 0 && (
          <Stack
            gap={0}
            flexShrink={0}
            textAlign={"right"}
            fontSize={"lg"}
            separator={<Separator borderColor={CHALK_MUTED} />}
          >
            {prices.map((price, index) => (
              <Text key={index} lineHeight={"1.2"}>
                {price}
              </Text>
            ))}
          </Stack>
        )}
      </Flex>
    </Box>
  );
}
