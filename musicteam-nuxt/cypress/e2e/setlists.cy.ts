declare global {
  namespace Cypress {
    interface Chainable {
      sidebarSong(
        inner: string,
        within: (el: JQuery<HTMLElement>) => void,
      ): Chainable<JQuery<HTMLElement>>
    }
  }
}

Cypress.Commands.add("sidebarSong", (inner, within) => {
  return cy.contains(inner).parents('[data-cy="sidebar-song"]').within(within)
})

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

    it("can add songs to setlist positions", () => {
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
        cy.sidebarSong("Test One (C)", () => {
          cy.dataCy("drop").click()
          cy.contains("First").click()
        })

        cy.sidebarSong("Test Two (C)", () => {
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
  })

  context("sheet operations", () => {
    beforeEach(() => {
      cy.prep("setlistWithCandidates")
    })

    it("can change song candidate state", () => {
      cy.get("@prep.setlist").then((id) => {
        cy.visit(`/setlists/${id}`)
        cy.exists("Test Title")
      })

      cy.sidebarSong("Song One", () => {
        cy.dataCy("state").should("have.prop", "title", "candidate")

        cy.dataCy("drop").click()
        cy.contains("Primary").should("not.exist")
        cy.contains("Secondary").should("not.exist")
        cy.contains("Extra").should("not.exist")

        cy.contains("Candidate (high)").click()
        cy.dataCy("state").should("have.prop", "title", "candidate-high")

        cy.dataCy("drop").click()
        cy.contains("Candidate (low)").click()
        cy.dataCy("state").should("have.prop", "title", "candidate-low")
      })

      cy.sidebarSong("Song Two", () => {
        cy.dataCy("state").should("have.prop", "title", "candidate")
        cy.dataCy("state").click()
        cy.dataCy("state").should("have.prop", "title", "candidate-high")
        cy.dataCy("state").click()
        cy.dataCy("state").should("have.prop", "title", "candidate-low")
        cy.dataCy("state").click()
        cy.dataCy("state").should("have.prop", "title", "candidate")
        cy.dataCy("state").click()
        cy.dataCy("state").should("have.prop", "title", "candidate-high")
      })

      cy.reload()

      cy.sidebarSong("Song One", () => {
        cy.dataCy("state").should("have.prop", "title", "candidate-low")
      })
      cy.sidebarSong("Song Two", () => {
        cy.dataCy("state").should("have.prop", "title", "candidate-high")
      })
    })

    it("can change song state", () => {
      cy.get("@prep.setlist").then((id) => {
        cy.visit(`/setlists/${id}`)
        cy.exists("Test Title")
      })
    })

    it("can swap song positions")
    it("can get lyrics packet")
  })
  // TODO:
  // - comments
  // - media
  // - edit set list details
  // - edit set list positions
})
