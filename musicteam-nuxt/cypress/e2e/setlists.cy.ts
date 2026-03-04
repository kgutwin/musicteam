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

  it("can delete a setlist", () => {
    cy.prep("setlist")
    cy.get("@prep.setlist").then((id) => {
      cy.visit(`/setlists/${id}`)
      cy.exists("Test Title")
    })

    cy.contains("Delete").click()

    cy.visit("/setlists")
    cy.contains("Test Title").should("not.exist")
  })

  context("editing setlists", () => {
    beforeEach(() => {
      cy.prep("setlist")
      cy.get("@prep.setlist").then((id) => {
        cy.visit(`/setlists/${id}`)
        cy.exists("Test Title")
      })
    })

    it("can edit setlist details", () => {
      cy.edit("service_date", ($el) => {
        $el.type("2026-01-06")
      }).should("contain.text", "1/6/2026")

      cy.edit("title", ($el) => {
        $el.type("{selectall}{del}New Title")
      }).should("contain.text", "New Title")

      cy.edit("leader_name", ($el) => {
        $el.type("{selectall}{del}Some Leader")
      }).should("contain.text", "Some Leader")

      cy.edit("participants", ($el) => {
        $el.find(".inp-array-newtag").type("{del}Joe,")
      })
        .should("contain.text", "Joe")
        .should("not.contain.text", "bar")

      cy.edit("tags", ($el) => {
        $el.find(".inp-array-newtag").type("TestTag{enter}")
      }).should("contain.text", "TestTag")

      cy.reload()

      cy.exists(["1/6/2026", "New Title", "Some Leader", "foo, Joe", "TestTag"])
    })

    it("can edit set list order inline", () => {
      cy.get("tbody tr:first").within(() => {
        cy.edit("presenter", ($el) => {
          $el.type("{selectall}{del}my name")
        }).should("contain.text", "my name")

        cy.edit("label", ($el) => {
          $el.type("{selectall}{del}First Song")
        }).should("contain.text", "First Song")
      })

      cy.get("tbody tr:nth-child(2)").within(() => {
        cy.edit("presenter", ($el) => {
          $el.type("{selectall}{del}some name")
        }).should("contain.text", "some name")

        cy.edit("label", ($el) => {
          $el.type("{selectall}{del}Next Part")
        }).should("contain.text", "Next Part")
      })

      cy.reload()

      cy.exists(["my name", "First Song", "some name", "Next Part"])
    })

    it("can edit set list order more", () => {
      cy.dataCy("edit-order").click()

      cy.get("tbody tr:first").within(() => {
        cy.edit("presenter", ($el) => {
          $el.type("{selectall}{del}my name")
        }).should("contain.text", "my name")

        cy.edit("label", ($el) => {
          $el.type("{selectall}{del}First Song")
        }).should("contain.text", "First Song")

        cy.dataCy("is-music").uncheck()

        cy.dataCy("add-position").click()
      })
      cy.exists("Label")

      cy.get("tbody tr:nth-child(2)")
        .should("contain.text", "Label")
        .within(() => {
          cy.edit("label", ($el) => {
            $el.type("{selectall}{del}New Part")
          }).should("contain.text", "New Part")

          cy.edit("presenter", ($el) => {
            $el.type("{selectall}{del}some name")
          }).should("contain.text", "some name")
        })

      cy.get("tbody tr:nth-child(3)").within(() => {
        cy.dataCy("is-music").check()
      })

      cy.get("tbody tr:last").within(() => {
        cy.dataCy("delete-position").click()
      })
      cy.contains("Last").should("not.exist")

      cy.reload()

      cy.exists(["my name", "First Song", "some name", "New Part", "Next"])
    })
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
        cy.exists("Test One")
      })

      cy.dataCy("to-setlist").click()
      cy.dataCy("toggle-panel").click()

      cy.exists("Test One")

      cy.reload()
      cy.exists("Test One")
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
        cy.sidebarSong("Test One", () => {
          cy.dataCy("drop").click()
          cy.contains("First").click()
        })

        cy.sidebarSong("Test Two", () => {
          cy.dataCy("drop").click()
          cy.contains("Last").click()
        })
      })

      cy.dataCy("sidebar-positions")
        .contains("First")
        .parents('[data-cy="sidebar-positions"]')
        .within(() => {
          cy.exists("Test One")
        })
      cy.dataCy("sidebar-positions")
        .contains("Last")
        .parents('[data-cy="sidebar-positions"]')
        .within(() => {
          cy.exists("Test Two")
        })

      cy.dataCy("to-setlist").click()
      cy.dataCy("toggle-panel").click()

      cy.contains("First").parents("tr").contains("Test One")
      cy.contains("Last").parents("tr").contains("Test Two")
    })
  })

  context("sheet operations", () => {
    beforeEach(() => {
      cy.prep("setlistWithCandidates")
      cy.get("@prep.setlist").then((id) => {
        cy.visit(`/setlists/${id}`)
        cy.exists("Test Title")
      })
    })

    it("can change song candidate state", () => {
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
      // assign songs to positions
      cy.sidebarSong("Song One", () => {
        cy.dataCy("drop").click()
        cy.contains("First").click()
      })

      cy.sidebarSong("Song Two", () => {
        cy.dataCy("drop").click()
        cy.contains("Last").click()
      })

      // now test
      cy.sidebarSong("Song One", () => {
        cy.dataCy("state").should("have.prop", "title", "candidate")

        cy.dataCy("drop").click()
        cy.contains("Primary").click()
        cy.dataCy("state").should("have.prop", "title", "primary")

        cy.dataCy("drop").click()
        cy.contains("Secondary").click()
        cy.dataCy("state").should("have.prop", "title", "secondary")

        cy.dataCy("drop").click()
        cy.contains("Extra").click()
        cy.dataCy("state").should("have.prop", "title", "extra")
      })

      cy.sidebarSong("Song Two", () => {
        cy.dataCy("state").should("have.prop", "title", "candidate")
        cy.dataCy("state").click()
        cy.dataCy("state").should("have.prop", "title", "primary")
        cy.dataCy("state").click()
        cy.dataCy("state").should("have.prop", "title", "secondary")
        cy.dataCy("state").click()
        cy.dataCy("state").should("have.prop", "title", "extra")
        cy.dataCy("state").click()
        cy.dataCy("state").should("have.prop", "title", "primary")
      })

      cy.reload()

      cy.sidebarSong("Song One", () => {
        cy.dataCy("state").should("have.prop", "title", "extra")
      })
      cy.sidebarSong("Song Two", () => {
        cy.dataCy("state").should("have.prop", "title", "primary")
      })
    })

    it("can swap song positions", () => {
      // assign songs to positions
      cy.sidebarSong("Song One", () => {
        cy.dataCy("drop").click()
        cy.contains("First").click()
      })

      cy.sidebarSong("Song Two", () => {
        cy.dataCy("drop").click()
        cy.contains("Last").click()
      })

      cy.reload()
      cy.get("tr").contains("First").parents("tr").contains("Song One")
      cy.get("tr").contains("Last").parents("tr").contains("Song Two")

      // now move them
      cy.sidebarSong("Song One", () => {
        cy.dataCy("drop").click()
        cy.contains("Last").click()
      })
      cy.get("tr").contains("Last").parents("tr").contains("Song One")

      cy.sidebarSong("Song Two", () => {
        cy.dataCy("drop").click()
        cy.contains("First").click()
      })
      cy.get("tr").contains("First").parents("tr").contains("Song Two")

      cy.reload()
      cy.get("tr").contains("Last").parents("tr").contains("Song One")
      cy.get("tr").contains("First").parents("tr").contains("Song Two")
    })

    context("packets", () => {
      beforeEach(() => {
        // assign songs to positions
        cy.sidebarSong("Song One", () => {
          cy.dataCy("drop").click()
          cy.contains("First").click()
        })

        cy.sidebarSong("Song Two", () => {
          cy.dataCy("drop").click()
          cy.contains("Last").click()
        })

        cy.sidebarSong("Song One", () => cy.dataCy("state").click())
        cy.sidebarSong("Song Two", () => cy.dataCy("state").click())
      })

      it("can get lyrics packet", () => {
        cy.contains("Lyrics Packet").click()
        cy.get('button[title="Warnings"]').should("not.exist")

        cy.get("object")
          .its("0.contentDocument.body")
          .should("not.be.empty")
          .then(cy.wrap)
          .within(() => {
            cy.exists([
              "# Set list for 2026-01-04",
              "** Song One **",
              "** Song Two **",
              "This has some basic lyrics.",
              "These are lyrics from the second song.",
            ])
          })
      })

      it("can get audience lyrics", () => {
        cy.visit("/lyrics")

        cy.exists(["Song One", "Song Two"])
        cy.contains("Song One").click()
        cy.exists("This has some basic lyrics.")
        cy.contains("Song Two").click()
        cy.exists("These are lyrics from the second song.")
      })
    })
  })

  context("comment ops", () => {
    beforeEach(() => {
      cy.prep("setlist")
      cy.get("@prep.setlist").then((id) => {
        cy.visit(`/setlists/${id}`)
        cy.contains("Test Title").should("exist")
      })
    })

    it("can add and delete a comment", () => {
      cy.contains("Comments").click()
      cy.dataCy("add-comment").click()
      cy.dataCy("post-comment").within(() => {
        cy.get("textarea").type("Test Cypress comment")
        cy.get("button").contains("Post").click()
      })

      cy.exists("Test Cypress comment")

      cy.reload()
      cy.contains("Comments").click()
      cy.exists("Test Cypress comment")

      cy.dataCy("delete-comment").click({ force: true })
      cy.contains("Test Cypress comment").should("not.exist")

      cy.reload()
      cy.contains("Comments").click()
      cy.contains("Test Cypress comment").should("not.exist")
    })
  })

  context("media ops", () => {
    beforeEach(() => {
      cy.prep("setlistWithCandidates")
      cy.get("@prep.setlist").then((id) => {
        cy.visit(`/setlists/${id}`)
        cy.exists("Test Title")
      })
    })

    it("can see song media in set list", () => {
      // assign songs to positions
      cy.sidebarSong("Song One", () => {
        cy.dataCy("drop").click()
        cy.contains("First").click()
      })

      cy.sidebarSong("Song Two", () => {
        cy.dataCy("drop").click()
        cy.contains("Last").click()
      })

      cy.contains("Media").click()

      cy.exists(["Test Link", "https://example.com", "Test Attach", "audio/mpeg"])
    })
  })
})
