describe("app init", () => {
  it("can load the home page", () => {
    cy.visit("http://localhost:3000")
    cy.contains("MusicTeam").should("exist")
  })

  it("can sign in", () => {
    cy.visit("http://localhost:3000/login")

    cy.contains("Sign in with Google").click()

    cy.contains("Local User").should("exist")
  })
})
