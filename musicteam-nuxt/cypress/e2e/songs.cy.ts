describe("songs", () => {
  beforeEach(() => {
    cy.login()
    cy.wipe()
  })

  it("can explore songs", () => {
    cy.prep("song")

    cy.visit("/songs")
    cy.exists("Test One").click()

    cy.exists("foo, bar")
    cy.exists("123456")

    cy.exists("From Cypress")
    cy.exists("V1 C1 V2 C1")

    cy.contains("Lyrics").click()
    cy.exists("This has some basic lyrics")

    cy.contains("Chord (C)").click()
    cy.exists("This is a basic text-formatted song sheet")

    cy.contains("Lead (C)").click()
    cy.get("object").should("exist")
  })

  context("editing songs", () => {
    beforeEach(() => {
      cy.prep("song")
      cy.get("@prep.song").then((id) => {
        cy.visit(`/songs/${id}`)
        cy.contains("Test One").should("exist")
      })
    })

    it("can edit song details", () => {
      cy.edit("title", ($el) => {
        $el.type("{selectall}{del}My Song Two")
      }).should("contain.text", "My Song Two")

      cy.edit("authors", ($el) => {
        $el.find(".inp-array-newtag").type("{del}Joe{enter}")
      })
        .should("contain.text", "Joe")
        .should("not.contain.text", "bar")

      cy.edit("ccli_num", ($el) => {
        $el.type("{selectall}{del}54321")
      }).should("contain.text", "54321")

      cy.edit("tags", ($el) => {
        $el.find(".inp-array-newtag").type("TestTag{enter}")
      }).should("contain.text", "TestTag")

      cy.reload()
      cy.exists(["My Song Two", "foo, Joe", "54321", "TestTag"])

      cy.visit("/songs")
      cy.exists(["My Song Two", "Joe", "TestTag"])
    })

    it("can edit version details", () => {
      cy.edit("label", ($el) => {
        $el.type("{selectall}{del}From Test")
      }).should("contain.text", "From Test")

      cy.edit("verse_order", ($el) => {
        $el.find(".inp-array-newtag").type("{del}{del}V3 C1 C2 V4{enter}")
      }).should("contain.text", "V1 C1 V3 C1 C2 V4")

      cy.reload()
      cy.exists(["From Test", "V1 C1 V3 C1 C2 V4"])

      // make sure lyrics are selected
      cy.get(".btn-tab").contains("Lyrics").click()
      cy.exists("Order: V1 C1 V3 C1 C2 V4")
    })

    it("can edit lyrics", () => {
      cy.get(".btn-tab").contains("Lyrics").click()
      cy.dataCy("edit-sheet").click()
      cy.get("button").contains("Edit Current Version").click()

      cy.formLabel("Label").select("Updated")
      cy.formLabel("Verse Order").within(() => {
        cy.get(".inp-array-newtag").type("V3 ")
      })

      cy.get("textarea.txt-panel").type("{selectall}{del}New Lyrics")

      cy.dataCy("save").click()

      cy.exists("CCLI Number")
      cy.exists(["Updated", "V1 C1 V2 C1 V3", "New Lyrics"])
    })

    it("can edit a text chord sheet", () => {
      cy.get(".btn-tab").contains("Chord (C)").click()
      cy.dataCy("edit-sheet").click()
      cy.get("button").contains("Edit Current Version").click()

      cy.formLabel("Music Sheet Type").select("Hymn")
      cy.formLabel("Musical Key").type("{selectall}{del}D")
      cy.formLabel("include verse order").select("Sheet already has verse order")

      cy.get("textarea.txt-panel").type("{selectall}{del}New song sheet")

      cy.dataCy("save").click()

      cy.exists("CCLI Number")
      cy.get(".btn-tab").contains("Hymn (D)").click()
      cy.exists("New song sheet")
    })

    it("can edit a PDF chord sheet", () => {
      cy.get(".btn-tab").contains("Lead (C)").click()
      cy.dataCy("edit-sheet").click()
      cy.get("button").contains("Edit Current Version").click()

      cy.formLabel("Music Sheet Type").select("Vocal")
      cy.formLabel("Musical Key").type("{selectall}{del}D")
      cy.formLabel("include verse order").select("Sheet already has verse order")

      cy.pdfjsViewerElement().within(() => {
        cy.get("#editorFreeTextButton").click()
        cy.get(".annotationEditorLayer").click().type("blah")
        cy.get("#editorFreeTextButton").click()
      })

      cy.dataCy("save").click()

      cy.exists(["CCLI Number", "Vocal (D)"])

      // Electron browser doesn't have PDF viewer; to confirm our annotation was
      // saved, we open the edit screen again

      cy.get(".btn-tab").contains("Vocal (D)").click()
      cy.dataCy("edit-sheet").click()
      cy.get("button").contains("Edit Current Version").click()

      cy.pdfjsViewerElement().within(() => {
        cy.exists("blah")
      })
    })
  })

  context("deleting songs", () => {
    beforeEach(() => {
      cy.prep("songMultiVersion")
      cy.get("@prep.song").then((id) => {
        cy.visit(`/songs/${id}`)
        cy.contains("Test Two").should("exist")
      })
    })

    it("can delete a song sheet", () => {
      cy.contains("From Cypress").click()

      cy.get(".btn-tab").contains("Chord (C)").click()
      cy.get("button").contains("Delete").click()
      cy.get("button").contains("Delete Sheet").click()

      cy.contains("Chord (C)").should("not.exist")
      cy.exists("Lead (C)")
    })

    it("can delete a song version", () => {
      cy.contains("From Cypress").click()

      cy.get("button").contains("Delete").click()
      cy.get("button").contains("Delete Version").click()

      cy.contains("From Cypress").should("not.exist")
      cy.exists("Alternate Version")
    })

    it("can delete an entire song", () => {
      cy.get("button").contains("Delete").click()
      cy.get("button").contains("Delete Song").click()

      cy.contains("Test Two").should("not.exist")
    })
  })
})
