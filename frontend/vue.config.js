module.exports = {
  transpileDependencies: ['langchain', 'langchainplus-sdk'], 
  chainWebpack: config => {
      config.module
          .rule('cjs')
          .test(/\.cjs$/)
          .use('babel-loader')
          .loader('babel-loader')
          .end()
  }
}