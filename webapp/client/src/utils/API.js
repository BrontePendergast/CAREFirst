import axios from "axios";

export default {
  sendQuery: function (query, conv_id) {
    const endpointUrl = `https://rmarin.mids255.com/conversations/${conv_id}`;
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
        console.log(conv_id);
        return {"answer": response['data']['answer'], "page": toString(response['data']['source']['page'])};
        // console.log(JSON.stringify(response)['data']['output']['answer']);
      })
      .catch((error) => {
        console.error(`Error: ${error.message}`);
        return {"answer": "I'm sorry, we could not process a response. Please try asking your question again.", "page": "N/A"};
      });
  },
};
