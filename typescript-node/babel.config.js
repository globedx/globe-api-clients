module.exports = {
  plugins: [
    "@babel/plugin-proposal-optional-chaining",
    "@babel/plugin-proposal-class-properties",
    "@babel/plugin-proposal-export-namespace-from",
  ],
  presets: [
    [
      "@babel/env",
      {
        targets: {
          node: "10",
        },
      },
    ],
    "@babel/typescript",
  ],
}
