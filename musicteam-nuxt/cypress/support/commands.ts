/// <reference types="cypress" />
import yaml from "yaml"

declare global {
  namespace Cypress {
    interface Chainable {
      login(dest?: string): Chainable<void>
      prep(fixture: string): Chainable<void>
      wipe(): Chainable<void>
    }
  }
}

Cypress.Commands.add("login", (dest) => {
  cy.request({ method: "GET", url: "/api/auth/callback", followRedirect: false }).then(
    (response) => {
      expect(response.status).to.equal(302)
    },
  )
  cy.visit("/login?complete=1")
  cy.contains("Local User").should("exist")
  cy.visit(dest ?? "/")
})

// Backend object fixtures

interface HasId {
  id: string
}

type FixtureType = "song" | "songVersion" | "songSheet" | "object"

type LinkRecord = { [Property in FixtureType]?: string }

const fixtureUrls: Record<FixtureType, (p: LinkRecord) => string> = {
  song: ($) => `/songs`,
  songVersion: ($) => `/songs/${$.song}/versions`,
  songSheet: ($) => `/songs/${$.song}/versions/${$.songVersion}/sheets`,
  object: ($) => `/objects?base64=true`,
}

interface FixtureObject {
  ref?: string
  type: FixtureType
  links?: LinkRecord
  data?: Record<string, any>
  file?: string
}

interface Fixture {
  objects: FixtureObject[]
}

Cypress.Commands.add("prep", (fixture) => {
  cy.fixture(fixture + ".yaml")
    .then((data: string) => yaml.parse(data).objects)
    .each((obj: FixtureObject) => {
      const ref = obj.ref ?? obj.type

      const links: LinkRecord = {}
      Object.entries(obj.links ?? {}).forEach(([ftype, fref]) => {
        cy.get(`@prep.${fref}`).then((v) => {
          links[ftype] = v
        })
      })

      const jsonData = obj.data ?? {}
      jsonData.tags = ["cypress", ...(jsonData.tags ?? [])]
      const fixtureData = obj.file ? cy.fixture(obj.file, "base64") : cy.wrap(jsonData)

      fixtureData.then((body) => {
        const headers: Record<string, string> = {}
        if (obj.file) {
          headers["content-type"] = "text/plain"
        } else {
          function applyLinks(o: Record<string, any>) {
            for (const k in o) {
              switch (typeof o[k]) {
                case "object":
                  applyLinks(o[k])
                  break
                case "string":
                  if (o[k].startsWith("!Ref ")) {
                    o[k] = links[o[k].substring(5)]
                  }
                  break
              }
            }
          }
          applyLinks(body)
        }

        const url = "/api" + fixtureUrls[obj.type](links)
        cy.request({ method: "POST", url, body, headers })
          .then((response) => response.body.id)
          .as(`prep.${ref}`)
      })
    })
})

Cypress.Commands.add("wipe", () => {
  cy.request({ url: "/api/songs" })
    .then((response) =>
      response.body.songs.filter((song) => song.tags.includes("cypress")),
    )
    .each((song: HasId) =>
      cy.request({ method: "DELETE", url: `/api/songs/${song.id}` }),
    )
})
