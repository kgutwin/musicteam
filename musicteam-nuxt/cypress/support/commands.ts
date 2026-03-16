/// <reference types="cypress" />
import yaml from "yaml"

declare global {
  namespace Cypress {
    interface Chainable {
      login(name?: string): Chainable<void>
      prep(fixture: string): Chainable<void>
      wipe(): Chainable<void>
      dataCy(label: string, extra?: string): Chainable<JQuery<HTMLElement>>
      edit(
        label: string,
        withEditable: (el: Chainable<JQuery<HTMLElement>>) => void,
      ): Chainable<JQuery<HTMLElement>>
      exists(text: string): Chainable<JQuery<HTMLElement>>
      exists(text: string[]): Chainable<void>
      formLabel(label: string): Chainable<JQuery<HTMLElement>>
      pdfjsViewerElement(): Chainable<JQuery<HTMLElement>>
    }
  }
}

Cypress.Commands.add("login", (name = "Local User") => {
  cy.session(
    name,
    () => {
      cy.request({
        method: "GET",
        url: "/api/auth/callback",
        qs: { name },
        followRedirect: false,
      }).then((response) => {
        expect(response.status).to.equal(302)
      })
      cy.visit("/login?complete=1")
      cy.contains(name).should("exist")
    },
    {
      validate() {
        cy.request("/api/auth/session").then((response) => {
          expect(response.body.name).to.equal(name)
        })
      },
    },
  )
})

// Backend object fixtures

interface HasId {
  id: string
}

type FixtureType =
  | "song"
  | "songVersion"
  | "songSheet"
  | "songMedia"
  | "object"
  | "setlist"
  | "setlistPosition"
  | "setlistSheet"

type LinkRecord = { [Property in FixtureType]?: string }

const fixtureUrls: Record<FixtureType, (p: LinkRecord) => string> = {
  song: ($) => `/songs`,
  songVersion: ($) => `/songs/${$.song}/versions`,
  songSheet: ($) => `/songs/${$.song}/versions/${$.songVersion}/sheets`,
  songMedia: ($) => `/songs/${$.song}/versions/${$.songVersion}/media`,
  object: ($) => `/objects?base64=true`,
  setlist: ($) => `/setlists`,
  setlistPosition: ($) => `/setlists/${$.setlist}/pos`,
  setlistSheet: ($) => `/setlists/${$.setlist}/sheets`,
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
  cy.request({ url: "/api/setlists" })
    .then((response) =>
      response.body.setlists.filter((setlist) => setlist.tags.includes("cypress")),
    )
    .each((setlist: HasId) =>
      cy.request({ method: "DELETE", url: `/api/setlists/${setlist.id}` }),
    )
  cy.request({ url: "/api/songs" })
    .then((response) =>
      response.body.songs.filter((song) => song.tags.includes("cypress")),
    )
    .each((song: HasId) =>
      cy.request({ method: "DELETE", url: `/api/songs/${song.id}` }),
    )
})

Cypress.Commands.add("dataCy", (label, extra) => {
  const tag = extra ? ` ${extra}` : ""
  return cy.get(`[data-cy="${label}"]${tag}`)
})

Cypress.Commands.add("edit", (prop, withEditable) => {
  cy.dataCy(`editable-${prop}`).within(() => {
    cy.dataCy("editing").click({ force: true })
    withEditable(cy.get(':has(+ [data-cy="save"])'))
    cy.dataCy("save").click()
  })
  return cy.dataCy(`editable-${prop}`)
})

Cypress.Commands.add("exists", (text) => {
  if (Array.isArray(text)) {
    text.forEach((v) => cy.contains(v).should("exist"))
  } else {
    return cy.contains(text).should("exist")
  }
})

Cypress.Commands.add("formLabel", (label) => {
  return cy.get("form label span").contains(label).next()
})

Cypress.Commands.add("pdfjsViewerElement", () => {
  return cy
    .get("pdfjs-viewer-element")
    .its("0.shadowRoot")
    .should("not.be.empty")
    .then(($el) =>
      cy
        .wrap($el)
        .find("iframe")
        .its("0.contentDocument.body")
        .should("not.be.empty")
        .then<JQuery<HTMLElement>>(cy.wrap),
    )
})
