import { QueryClientProvider } from "@tanstack/react-query";
import { useMemo } from "react";
import { RouterProvider } from "react-router-dom";

import { createAppRouter } from "./router";
import { createQueryClient } from "./queryClient";

type AppProps = {
  router?: ReturnType<typeof createAppRouter>;
};

export function App({ router }: AppProps) {
  const queryClient = useMemo(() => createQueryClient(), []);
  const appRouter = useMemo(() => router ?? createAppRouter(), [router]);

  return (
    <QueryClientProvider client={queryClient}>
      <RouterProvider router={appRouter} />
    </QueryClientProvider>
  );
}

export default App;
