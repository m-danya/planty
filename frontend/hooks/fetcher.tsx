import axios from "axios";

export const fetcher = (url: string) =>
  axios
    .get(url)
    .then((res) => res.data)
    .catch((error) => {
      if (error.response && error.response.status !== 401) {
        alert(`An error occurred while fetching ${url}: ${error.message}`);
      }
      throw error;
    });
