import createClient from "openapi-fetch";

import { API_URL } from "../constants";
import type { paths } from "./schema";

export const client = createClient<paths>({ baseUrl: API_URL });
