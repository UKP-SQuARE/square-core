module.exports = {
  // These libraries need to be transpiled with Babel. 
  // Use this when you see the error: You may need an appropriate loader to handle this file type ... 
  transpileDependencies: ["langchain", "langchainplus-sdk", "@smithy", "@aws-sdk"],
  chainWebpack: (config) => {
    config.module
      .rule("cjs")
      .test(/\.cjs$/)
      .use("babel-loader")
      .loader("babel-loader")
      .end();
  }
};
