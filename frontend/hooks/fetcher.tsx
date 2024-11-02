export const fetcher = async (url: string) => {
  const response = await fetch(url);
  if (!response.ok) {
    const error = new Error(`Error fetching ${url}: ${response.statusText}`);
    (error as any).status = response.status;
    throw error;
  }
  return response.json();
};
