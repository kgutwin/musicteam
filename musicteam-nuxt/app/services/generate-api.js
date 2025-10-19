import path from "path"
import { generateApi } from "swagger-typescript-api"
import _ from "lodash"

generateApi({
  input: path.resolve(process.cwd(), "../musicteam-api.yaml"),
  output: path.resolve(process.cwd(), "./app/services"),
  fileName: "api.ts",
  hooks: {
    onFormatRouteName: (routeInfo) => {
      const operation = routeInfo.operationId.split(".").pop()
      return _.camelCase(operation)
    },
  },
})
