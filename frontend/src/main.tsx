import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import {
  ChakraProvider,
  createSystem,
  defaultConfig,
  defineConfig,
} from "@chakra-ui/react";
import "@fontsource/caveat/400.css";
import "@fontsource/caveat/600.css";
import "@fontsource/caveat/700.css";
import App from "./App.tsx";

const system = createSystem(
  defaultConfig,
  defineConfig({
    theme: {
      tokens: {
        fonts: {
          heading: { value: '"Caveat", ui-rounded, cursive' },
        },
      },
    },
    globalCss: {
      body: {
        backgroundColor: "#8a4621",
        backgroundImage: 'url("/brick.svg")',
        backgroundRepeat: "repeat",
        backgroundSize: "120px 112px",
      },
    },
  }),
);

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <ChakraProvider value={system}>
      <App />
    </ChakraProvider>
  </StrictMode>,
);
