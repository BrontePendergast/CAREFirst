import axios from "axios";

export default {
  sendQuery: function (query) {
    const uniqueId = Math.floor(Date.now() / 1000)
    const endpointUrl = `https://rmarin.mids255.com/conversations/${uniqueId}`;
    return axios
      .post(
        endpointUrl,
        {
          query: query,
        },
        {
          headers: {
            'Content-Type': 'application/json',
          },
          withCredentials: true,
        }
      )
      .then((response) => {
        // console.log(response['data']['output']['answer']);
        // console.log(response['data']['answer']);
        // return response['data']['output']['answer'];
        return response['data']['answer'];
        // console.log(JSON.stringify(response)['data']['output']['answer']);
      })
      .catch((error) => {
        console.error(`Error: ${error.message}`);
      });
  },
};
