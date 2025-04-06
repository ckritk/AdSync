const express = require('express');
const ports = [4001, 4002, 4003];
const redirectUrl = 'https://30g468db-3000.inc1.devtunnels.ms/PT037lpXo';

ports.forEach(port => {
  const app = express();

  app.get('/', (req, res) => {
    res.send(`<!DOCTYPE html>
      <html>
      <head>
        <title>Redirect Page on Port ${port}</title>
      </head>
      <body>
        <h2>Page on Port ${port}</h2>
        <a href="${redirectUrl}">Go to Redirect</a>
      </body>
      </html>`);
  });

  app.listen(port, () => {
    console.log(`Server running on http://localhost:${port}`);
  });
});
