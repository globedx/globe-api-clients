module.exports = {
  arrowParens: "always",
  proseWrap: "always",
  trailingComma: "all",
  semi: false,
  overrides: [
    {
      files: "*.js",
      options: {
        parser: "babel",
      },
    },
    {
      files: "*.md",
      options: {
        parser: "markdown",
      },
    },
    {
      files: "*.scss",
      options: {
        parser: "scss",
      },
    },
    {
      files: "*.ts",
      options: {
        parser: "typescript",
      },
    },
    {
      files: "*.tsx",
      options: {
        parser: "typescript",
      },
    },
    {
      files: "*.yml",
      options: {
        parser: "yaml",
      },
    },
  ],
}
