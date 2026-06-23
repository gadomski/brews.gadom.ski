import { Center, Heading, HStack } from "@chakra-ui/react";

import { CHALK } from "../constants";
import { BrewsIcon } from "./BrewsIcon";

export default function Header() {
  return (
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
  );
}
