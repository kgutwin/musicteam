describe("user management", () => {
  it("can put new users into pending state", () => {
    cy.login("Pending User")
    cy.visit("/songs")
    cy.exists("need to approve your membership")

    cy.login()
    cy.visit("/team")
    cy.contains("tr", "Pending User").within(() => {
      cy.dataCy("role-editable").should("contain.text", "pending")
    })
  })

  context("viewer users", () => {
    beforeEach(() => {
      cy.login()
      cy.wipe()
      cy.prep("setlistWithCandidates")

      cy.login("Viewer User")
      cy.request("/api/auth/session").then((response) => {
        if (response.body.role !== "viewer") {
          // grant the user viewer status
          Cypress.session.clearAllSavedSessions()
          cy.login()
          cy.request("PUT", `/api/users/${response.body.id}`, { role: "viewer" })
          cy.login("Viewer User")
        }
      })
    })

    it("can view songs as a viewer", () => {
      cy.visit("/songs")
      cy.contains("New...").should("not.exist")
      cy.contains("Song One").click()

      cy.exists(["CCLI Number", "From Cypress", "V1 C1 V2 C1", "Lead (C)"])
      cy.contains("Delete").should("not.exist")
      cy.contains("Add").should("not.exist")
      cy.contains("Edit").should("not.exist")

      cy.contains("Media").click()
      cy.exists(["Test Link", "https://example.com"])

      // can leave a comment
      cy.dataCy("add-comment").click()
      cy.dataCy("post-comment").within(() => {
        cy.get("textarea").type("Test viewer comment")
        cy.contains("button", "Post").click()
      })
      cy.exists("Test viewer comment")
      cy.dataCy("delete-comment").click({ force: true })
      cy.contains("Test viewer comment").should("not.exist")
    })

    it("can search songs as a viewer", () => {
      cy.visit("/songs/search")
      cy.get("input[type=search]").type("basic{enter}")

      cy.exists(["Song One", "some basic lyrics"])
    })

    it("can view set lists as a viewer", () => {
      cy.visit("/setlists")
      cy.contains("New...").should("not.exist")
      cy.contains("Test Title").click()

      cy.exists(["First", "Next", "Last"])
    })
  })
})
