import axios from "axios";

export default {
  sendQuery: function (query) {
    return axios
      .post(
        'http://localhost:8000/conversations/9999/',
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
        console.log(response['data']['output']['answer']);
        return response['data']['output']['answer'];
        // console.log(JSON.stringify(response)['data']['output']['answer']);
      })
      .catch((error) => {
        console.error(`Error: ${error.message}`);
      });
  },
};
