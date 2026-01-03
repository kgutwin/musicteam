describe("setlists", () => {
  beforeEach(() => {
    cy.login()
    cy.wipe()
  })

  it("can explore set lists", () => {
    cy.prep("setlist")
    cy.visit("/setlists")

    cy.exists(["Cypress", "Test Title", "foo", "bar"])
    cy.contains("Test Title").click()

    cy.exists(["1/4/2026", "Test Title", "Cypress", "foo, bar"])
    cy.exists(["someone", "First", "Next", "Last"])
  })

  context("adding songs", () => {
    beforeEach(() => {
      cy.prep("song")
      cy.prep("songMultiVersion")
      cy.prep("setlist")
    })

    it("can add a song as a candidate", () => {
      cy.get("@prep.setlist").then((id) => {
        cy.visit(`/setlists/${id}`)
        cy.exists("Test Title")
      })
      cy.contains("Make Active").click()

      cy.contains("Find songs").click()
      cy.contains("Test One").click()

      cy.contains("Chord (C)").click()
      cy.contains("Add as Candidate").click()

      cy.dataCy("sidebar-candidates").within(() => {
        cy.exists("Test One (C)")
      })

      cy.dataCy("to-setlist").click()
      cy.dataCy("toggle-panel").click()

      cy.exists("Test One (C)")

      cy.reload()
      cy.exists("Test One (C)")
    })

    it.only("can add songs to setlist positions", () => {
      cy.get("@prep.setlist").then((id) => {
        cy.visit(`/setlists/${id}`)
        cy.exists("Test Title")
      })
      cy.contains("Make Active").click()

      cy.contains("Find songs").click()
      cy.contains("Test One").click()

      cy.contains("Chord (C)").click()
      cy.contains("Add as Candidate").click()

      cy.contains("Find songs").click()
      cy.contains("Test Two").click()
      cy.contains("From Cypress").click()

      cy.contains("Lead (C)").click()
      cy.contains("Add as Candidate").click()

      cy.dataCy("sidebar-candidates").within(() => {
        cy.exists("Test One (C)")
          .parents('[data-cy="sidebar-song"]')
          .within(() => {
            cy.dataCy("drop").click()
            cy.contains("First").click()
          })

        cy.exists("Test Two (C)")
          .parents('[data-cy="sidebar-song"]')
          .within(() => {
            cy.dataCy("drop").click()
            cy.contains("Last").click()
          })
      })

      cy.dataCy("sidebar-positions")
        .contains("First")
        .parents('[data-cy="sidebar-positions"]')
        .within(() => {
          cy.exists("Test One (C)")
        })
      cy.dataCy("sidebar-positions")
        .contains("Last")
        .parents('[data-cy="sidebar-positions"]')
        .within(() => {
          cy.exists("Test Two (C)")
        })

      cy.dataCy("to-setlist").click()
      cy.dataCy("toggle-panel").click()

      cy.contains("First").parents("tr").contains("Test One (C)")
      cy.contains("Last").parents("tr").contains("Test Two (C)")
    })
    // TODO:
    // - toggle song state
    // - move songs around
    // - check lyrics packet
    // - comments
    // - media
    // - edit set list details
    // - edit set list positions
  })
})
