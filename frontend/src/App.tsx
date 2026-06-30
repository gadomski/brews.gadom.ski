import {
  Alert,
  Box,
  Button,
  ButtonGroup,
  Center,
  Container,
  Dialog,
  EmptyState,
  FileUpload,
  Flex,
  HStack,
  Heading,
  IconButton,
  Popover,
  Portal,
  Separator,
  SimpleGrid,
  Skeleton,
  Stack,
  Steps,
  Text,
} from "@chakra-ui/react";
import { useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { LuBeer, LuCamera, LuLoader, LuLogIn, LuUpload } from "react-icons/lu";

import { type Beer } from "./api";
import { client } from "./api/client";
import { BrewsIcon } from "./components/BrewsIcon";
import { PasswordInput } from "./components/ui/password-input";
import useBeers from "./hooks/useBeers";

export default function App() {
  const result = useBeers();
  const [token, setToken] = useState<string>();

  return (
    <Container py={8}>
      <Stack>
        <Center>
          <HStack gap={3}>
            <BrewsIcon />
            <Heading lineHeight={1}>Shoes & Brews</Heading>
          </HStack>
        </Center>
        {result.isLoading && <Skeleton h={20} />}
        {result.isError && <Error error={result.error} />}
        {result.data &&
          (result.data.length === 0 ? (
            <Empty />
          ) : (
            <Beers beers={result.data} />
          ))}
      </Stack>
      <ButtonGroup position="fixed" bottom={4} right={4} variant={"ghost"}>
        {token ? (
          <UploadButton token={token} />
        ) : (
          <LoginButton setToken={setToken} />
        )}
      </ButtonGroup>
    </Container>
  );
}

function Error({ error }: { error: Error }) {
  return (
    <Alert.Root status={"error"}>
      <Alert.Indicator />
      <Alert.Content>
        <Alert.Title>Error</Alert.Title>
        <Alert.Description>{error.message}</Alert.Description>
      </Alert.Content>
    </Alert.Root>
  );
}

function Empty() {
  return (
    <EmptyState.Root>
      <EmptyState.Content>
        <EmptyState.Indicator>
          <LuBeer />
        </EmptyState.Indicator>
        <EmptyState.Title>No beers found</EmptyState.Title>
      </EmptyState.Content>
    </EmptyState.Root>
  );
}

function Beers({ beers }: { beers: Beer[] }) {
  return (
    <SimpleGrid columns={{ base: 1, md: 4 }}>
      {beers.map((beer, i) => (
        <Beer key={i} beer={beer} />
      ))}
    </SimpleGrid>
  );
}

function Beer({ beer }: { beer: Beer }) {
  return (
    <Box px={3} py={4}>
      <Flex justify={"space-between"} gap={3}>
        <Box>
          <Heading>{beer.name}</Heading>
          <Text color="fg.muted" fontSize={"sm"}>
            {[beer.brewery, beer.style, beer.abv ? `${beer.abv}%` : null]
              .filter(Boolean)
              .join(" · ")}
          </Text>
        </Box>
        {beer.prices && beer.prices.length > 0 && (
          <Stack
            gap={0}
            textAlign={"right"}
            fontSize={"xs"}
            color={"fg.muted"}
            separator={<Separator />}
          >
            {beer.prices.map((price, index) => (
              <Text key={index}>{price}</Text>
            ))}
          </Stack>
        )}
      </Flex>
    </Box>
  );
}

function LoginButton({ setToken }: { setToken: (token: string) => void }) {
  const [value, setValue] = useState("");
  const [isValidating, setIsValidating] = useState(false);
  const [error, setError] = useState<boolean>(false);

  async function validateToken(token: string) {
    setIsValidating(true);
    try {
      const { error } = await client.GET("/validate-token", {
        params: { query: { token } },
      });
      if (error) {
        setError(true);
      } else {
        setToken(token);
      }
    } finally {
      setIsValidating(false);
    }
  }

  return (
    <Popover.Root>
      <Popover.Trigger asChild>
        <IconButton disabled={isValidating}>
          {isValidating ? <LuLoader /> : <LuLogIn />}
        </IconButton>
      </Popover.Trigger>
      <Portal>
        <Popover.Positioner>
          <Popover.Content>
            <Popover.Arrow />
            <Popover.Body>
              <Popover.Title fontWeight={"medium"}>Set token</Popover.Title>
              {error ? (
                <Text color={"red"} my={4}>
                  If you don't know the token, ask Pete
                </Text>
              ) : null}
              <form
                onSubmit={(event) => {
                  event.preventDefault();
                  validateToken(value);
                }}
              >
                <PasswordInput
                  value={value}
                  onChange={(event) => setValue(event.target.value)}
                />
              </form>
            </Popover.Body>
          </Popover.Content>
        </Popover.Positioner>
      </Portal>
    </Popover.Root>
  );
}

function UploadButton({ token }: { token: string }) {
  const queryClient = useQueryClient();
  const [step, setStep] = useState<number>();
  const [error, setError] = useState<string>();

  const steps = [
    { title: "Prepare", description: "Preparing the upload" },
    { title: "Upload", description: "Uploading the picture" },
    { title: "Process", description: "Processing the picture" },
  ];

  async function uploadFile(file: File) {
    setError(undefined);
    try {
      setStep(1);
      const { data, error } = await client.POST("/beers/upload-url", {
        params: { query: { content_type: file.type } },
        headers: { Authorization: `Bearer ${token}` },
      });
      if (error || !data) {
        throw "Failed to prepare the upload";
      }

      setStep(2);
      const response = await fetch(data.url, {
        method: "PUT",
        headers: { "Content-Type": file.type },
        body: file,
      });
      if (!response.ok) {
        throw `Failed to upload the picture (${response.status})`;
      }

      setStep(3);
      const { error: processError } = await client.POST("/beers/process", {
        params: { query: { key: data.key } },
        headers: { Authorization: `Bearer ${token}` },
      });
      if (processError) {
        throw "Failed to process the picture";
      }

      await queryClient.invalidateQueries({ queryKey: ["beers"] });
    } catch (error) {
      setError(typeof error === "string" ? error : "Something went wrong");
    } finally {
      setStep(undefined);
    }
  }

  return (
    <Dialog.Root>
      <Dialog.Trigger asChild>
        <IconButton>
          <LuUpload />
        </IconButton>
      </Dialog.Trigger>
      <Portal>
        <Dialog.Backdrop />
        <Dialog.Positioner>
          <Dialog.Content>
            <Dialog.Header>
              <Dialog.Title>Update the board</Dialog.Title>
            </Dialog.Header>
            <Dialog.Body>
              <Stack gap={4}>
                <FileUpload.Root
                  maxFiles={1}
                  accept={["image/*"]}
                  capture="environment"
                  onFileAccept={(details) => {
                    const file = details.files[0];
                    uploadFile(file);
                  }}
                >
                  <FileUpload.HiddenInput />
                  <FileUpload.Trigger asChild>
                    <Button variant={"outline"}>
                      <LuCamera /> Add picture
                    </Button>
                  </FileUpload.Trigger>
                  <FileUpload.List />
                </FileUpload.Root>
                {step && (
                  <Steps.Root step={step - 1} count={steps.length}>
                    <Steps.List>
                      {steps.map((step, index) => (
                        <Steps.Item
                          key={index}
                          index={index}
                          title={step.title}
                        >
                          <Steps.Indicator />
                          <Steps.Title>{step.title}</Steps.Title>
                          <Steps.Separator />
                        </Steps.Item>
                      ))}
                    </Steps.List>

                    {steps.map((step, index) => (
                      <Steps.Content key={index} index={index}>
                        {step.description}
                      </Steps.Content>
                    ))}

                    <Steps.CompletedContent>
                      Update complete!
                    </Steps.CompletedContent>
                  </Steps.Root>
                )}
                {error && <Text color={"red"}>{error}</Text>}
              </Stack>
            </Dialog.Body>
          </Dialog.Content>
        </Dialog.Positioner>
      </Portal>
    </Dialog.Root>
  );
}
