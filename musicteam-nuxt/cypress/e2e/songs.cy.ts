describe("songs", () => {
  it("can explore songs", () => {
    cy.login()
    cy.wipe()
    cy.prep("song")

    cy.visit("/songs")
    cy.contains("Test One").should("exist")
    cy.contains("Test One").click()

    cy.contains("foo, bar").should("exist")
    cy.contains("123456").should("exist")

    cy.contains("From Cypress").should("exist")
    cy.contains("V1 C1 V2 C1").should("exist")

    cy.contains("Lyrics").click()
    cy.contains("This has some basic lyrics").should("exist")

    cy.contains("Chord (C)").click()
    cy.contains("This is a basic text-formatted song sheet").should("exist")

    cy.contains("Lead (C)").click()
    cy.get("object").should("exist")
  })
})
