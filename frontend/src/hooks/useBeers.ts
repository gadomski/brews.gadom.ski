import { useQuery } from "@tanstack/react-query";

import { fetchBeers } from "../api";

export default function useBeers() {
  return useQuery({
    queryKey: ["beers"],
    queryFn: async () => {
      return fetchBeers();
    },
  });
}
