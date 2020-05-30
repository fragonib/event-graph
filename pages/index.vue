<template>
  <div class="container">
    <button v-if="isButtonShown" @click="loadGraph()">A grafear!</button>
    <div id="graph"></div>
  </div>
</template>

<script>
import * as vis from 'vis'
import { GRAPH } from '@/constants/graph'

export default {
  name: 'Home',
  data: () => ({
    isButtonShown: true,
    DOTstring: GRAPH
  }),
  methods: {
    loadGraph() {
      this.isButtonShown = false
      const container = document.getElementById('graph')

      const parsedData = vis.network.convertDot(this.DOTstring)

      const data = {
        nodes: parsedData.nodes,
        edges: parsedData.edges
      }

      const options = parsedData.options

      // you can extend the options like a normal JSON variable:
      options.nodes = {}

      // create a network
      // eslint-disable-next-line no-unused-vars
      const network = new vis.Network(container, data, options)
    }
  }
}
</script>

<style>
.container {
  margin: 0 auto;
  min-height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  text-align: center;
}

.title {
  font-family: 'Quicksand', 'Source Sans Pro', -apple-system, BlinkMacSystemFont,
    'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
  display: block;
  font-weight: 300;
  font-size: 100px;
  color: #35495e;
  letter-spacing: 1px;
}

.subtitle {
  font-weight: 300;
  font-size: 42px;
  color: #526488;
  word-spacing: 5px;
  padding-bottom: 15px;
}

.links {
  padding-top: 15px;
}
</style>
