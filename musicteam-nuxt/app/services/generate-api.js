import path from "path"
import { generateApi } from "swagger-typescript-api"
import _ from "lodash"

generateApi({
  input: path.resolve(process.cwd(), "../musicteam-api.yaml"),
  output: path.resolve(process.cwd(), "./app/services"),
  fileName: "api.ts",
  hooks: {
    onFormatRouteName: (routeInfo) => {
      let operation = routeInfo.operationId.split(".").pop()
      if (routeInfo.operationId === "auth.auth_session" && routeInfo.method !== "get") {
        operation += `_${routeInfo.method}`
      }
      return _.camelCase(operation)
    },
  },
})
