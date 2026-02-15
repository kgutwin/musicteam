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
        $el.find(".inp-array-newtag").type("{del}Joe,")
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
        $el.find(".inp-array-newtag").type("{del}{del}V3 C1 C2 V4 ")
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

  context("copying songs", () => {
    beforeEach(() => {
      cy.prep("song")
      cy.get("@prep.song").then((id) => {
        cy.visit(`/songs/${id}`)
        cy.contains("Test One").should("exist")
      })
    })

    it("can copy a version without a sheet", () => {
      cy.get(".btn-tab").contains("Lyrics").click()
      cy.dataCy("edit-sheet").click()
      cy.get("button").contains("Copy to New Version").click()

      cy.formLabel("Label").select("Updated")
      cy.formLabel("Verse Order").within(() => {
        cy.get(".inp-array-newtag").type("V3 ")
      })

      cy.get("textarea.txt-panel").type("{selectall}{del}New Lyrics")

      cy.dataCy("save").click()

      cy.exists("CCLI Number")
      cy.exists(["From Cypress", "Updated", "V1 C1 V2 C1 V3", "New Lyrics"])
      cy.contains("Chord").should("not.exist") // no sheets yet
    })

    it("can copy a version with a text chord sheet", () => {
      cy.get(".btn-tab").contains("Chord (C)").click()
      cy.dataCy("edit-sheet").click()
      cy.get("button").contains("Copy to New Version").click()

      cy.formLabel("Label").select("Updated")
      cy.formLabel("Verse Order").within(() => {
        cy.get(".inp-array-newtag").type("V3 ")
      })

      cy.formLabel("Music Sheet Type").select("Hymn")
      cy.formLabel("Musical Key").type("{selectall}{del}D")
      cy.formLabel("include verse order").select("Sheet already has verse order")

      cy.dataCy("song-lyrics-editor").type("{selectall}{del}Some New Lyrics")
      cy.dataCy("song-text-editor").type("{selectall}{del}Edited song sheet")

      cy.dataCy("save").click()

      cy.exists("CCLI Number")
      cy.get(".btn-tab").contains("Hymn (D)").click()
      cy.exists(["Edited song sheet", "From Cypress", "Updated", "V1 C1 V2 C1 V3"])
      cy.contains(".btn-tab", "Lyrics").click()
      cy.exists("Some New Lyrics")
    })

    it("can copy a version with a PDF chord sheet", () => {
      cy.get(".btn-tab").contains("Lead (C)").click()
      cy.dataCy("edit-sheet").click()
      cy.get("button").contains("Copy to New Version").click()

      cy.formLabel("Label").select("Updated")
      cy.formLabel("Verse Order").within(() => {
        cy.get(".inp-array-newtag").type("V3 ")
      })

      cy.formLabel("Music Sheet Type").select("Hymn")
      cy.formLabel("Musical Key").type("{selectall}{del}E")
      cy.formLabel("include verse order").select("Sheet already has verse order")

      cy.dataCy("song-lyrics-editor").type("{selectall}{del}Some New Lyrics")

      cy.pdfjsViewerElement().within(() => {
        cy.get("#editorFreeTextButton").click()
        cy.get(".annotationEditorLayer").click().type("blah")
        cy.get("#editorFreeTextButton").click()
      })

      cy.dataCy("save").click()

      cy.exists(["CCLI Number", "From Cypress", "Updated", "V1 C1 V2 C1 V3"])
      cy.contains(".btn-tab", "Lyrics").click()
      cy.exists("Some New Lyrics")

      // Electron browser doesn't have PDF viewer; to confirm our annotation was
      // saved, we open the edit screen again

      cy.get(".btn-tab").contains("Hymn (E)").click()
      cy.dataCy("edit-sheet").click()
      cy.get("button").contains("Edit Current Version").click()

      cy.pdfjsViewerElement().within(() => {
        cy.exists("blah")
      })
    })

    it("can copy a text chord sheet", () => {
      cy.get(".btn-tab").contains("Chord (C)").click()
      cy.dataCy("edit-sheet").click()
      cy.get("button").contains("Copy to New Sheet").click()

      cy.formLabel("Music Sheet Type").select("Hymn")
      cy.formLabel("Musical Key").type("{selectall}{del}D")
      cy.formLabel("include verse order").select("Sheet already has verse order")

      cy.get("textarea.txt-panel").type("{selectall}{del}New song sheet")

      cy.dataCy("save").click()

      cy.exists(["CCLI Number", "Chord (C)", "Lead (C)"])
      cy.get(".btn-tab").contains("Hymn (D)").click()
      cy.exists("New song sheet")
    })

    it("can copy a PDF chord sheet", () => {
      cy.get(".btn-tab").contains("Lead (C)").click()
      cy.dataCy("edit-sheet").click()
      cy.get("button").contains("Copy to New Sheet").click()

      cy.formLabel("Music Sheet Type").select("Vocal")
      cy.formLabel("Musical Key").type("{selectall}{del}D")
      cy.formLabel("include verse order").select("Sheet already has verse order")

      cy.pdfjsViewerElement().within(() => {
        cy.get("#editorFreeTextButton").click()
        cy.get(".annotationEditorLayer").click().type("blah")
        cy.get("#editorFreeTextButton").click()
      })

      cy.dataCy("save").click()

      cy.exists(["CCLI Number", "Chord (C)", "Lead (C)", "Vocal (D)"])

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
      cy.contains("From Cypress").click()
    })

    it("can delete a song sheet", () => {
      cy.get(".btn-tab").contains("Chord (C)").click()
      cy.get("button").contains("Delete").click()
      cy.get("button").contains("Delete Sheet").click()

      cy.contains("Chord (C)").should("not.exist")
      cy.exists("Lead (C)")
    })

    it("can delete a song version", () => {
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

  context("adding songs", () => {
    it("can add a song", () => {
      cy.visit("/songs/new")

      cy.formLabel("Title").type("Cypress Song")
      cy.formLabel("Authors").within(() => {
        cy.get(".inp-array-newtag").type("Joe Smith,Jane Test")
      })
      cy.formLabel("CCLI Number").type("121212")
      cy.formLabel("Tags").within(() => {
        cy.get(".inp-array-newtag").type("cypress ")
      })

      cy.formLabel("Version Label").select("Updated")
      cy.formLabel("Verse Order").within(() => {
        cy.get(".inp-array-newtag").type("V1 C1 V2 C1 V3 C2 ")
      })
      cy.get("textarea").type("Cypress Song\n\nVerse 1\nTest one two three\n")

      cy.formLabel("Music Sheet Type").select("Chord")
      cy.formLabel("Musical Key").type("D")
      cy.formLabel("Select File")
        .find("input")
        .selectFile("cypress/fixtures/song-sheet.pdf")

      cy.get("button").contains("Add another sheet").click()

      cy.get("form")
        .last()
        .within(() => {
          cy.get("label span").contains("Music Sheet Type").next().select("Lead")
          cy.get("label span").contains("Musical Key").next().type("D")
          cy.get("label span")
            .contains("Select File")
            .next()
            .find("input")
            .selectFile("cypress/fixtures/song-sheet.txt")
        })

      cy.get("button").contains("Save").click()

      cy.exists([
        "Cypress Song",
        "Joe Smith",
        "Jane Test",
        "121212",
        "Updated",
        "V1 C1 V2 C1 V3 C2",
        "Chord (D)",
        "Lead (D)",
        "Test one two three",
      ])

      cy.contains("Lead (D)").click()
      cy.exists("This is a basic text-formatted song sheet.")
    })
  })

  context("comment ops", () => {
    beforeEach(() => {
      cy.prep("songMultiVersion")
      cy.get("@prep.song").then((id) => {
        cy.visit(`/songs/${id}`)
        cy.contains("Test Two").should("exist")
      })
      cy.contains("From Cypress").click()
    })

    it("can add and delete a comment", () => {
      cy.contains("Comments").click()
      cy.dataCy("add-comment").click()
      cy.dataCy("post-comment").within(() => {
        cy.get("textarea").type("Test Cypress comment")
        cy.get("button").contains("Post").click()
      })

      cy.exists("Test Cypress comment")
      cy.contains("Alternate Version").click()
      cy.contains("Test Cypress comment").should("not.exist")

      cy.reload()
      cy.contains("From Cypress").click()
      cy.contains("Comments").click()
      cy.exists("Test Cypress comment")

      cy.dataCy("delete-comment").click({ force: true })
      cy.contains("Test Cypress comment").should("not.exist")

      cy.reload()
      cy.contains("From Cypress").click()
      cy.contains("Comments").click()
      cy.contains("Test Cypress comment").should("not.exist")
    })
  })

  context("media ops", () => {
    beforeEach(() => {
      cy.prep("songMultiVersion")
      cy.get("@prep.song").then((id) => {
        cy.visit(`/songs/${id}`)
        cy.contains("Test Two").should("exist")
      })
      cy.contains("From Cypress").click()
    })

    it("can add and delete a media attachment", () => {
      cy.contains("Media").click()

      cy.dataCy("add-media").click()
      cy.dataCy("post-media").within(() => {
        cy.dataCy("title").type("Test URL")
        cy.dataCy("url").type("https://www.example.com")
        cy.dataCy("tags").find(".inp-array-newtag").type("media-tag,media-gg")
        cy.dataCy("add").click()
      })

      cy.dataCy("add-media").click()
      cy.dataCy("post-media").within(() => {
        cy.dataCy("title").type("Test Attach")
        cy.dataCy("file").selectFile("cypress/fixtures/test.mp3")
        cy.dataCy("cancel-file").should("exist")
        cy.dataCy("add").click()
      })

      cy.exists([
        "Test URL",
        "https://www.example.com",
        "media-tag",
        "media-gg",
        "Test Attach",
        "audio/mpeg",
      ])

      cy.contains("Alternate Version").click()
      cy.contains("Test URL").should("not.exist")

      cy.reload()
      cy.contains("From Cypress").click()
      cy.contains("Media").click()
      cy.exists([
        "Test URL",
        "https://www.example.com",
        "media-tag",
        "media-gg",
        "Test Attach",
        "audio/mpeg",
      ])

      // kgutwin 2026-01-01  this isn't working in electron for some reason
      // cy.dataCy("download-media").click()
      // const downloadsFolder = Cypress.config("downloadsFolder")
      // cy.readFile(`${downloadsFolder}/Test Two - Test Attach.mp3`)

      cy.dataCy("delete-media").first().click({ force: true })
      cy.contains("Test URL").should("not.exist")
      cy.dataCy("delete-media").click({ force: true })

      cy.contains("Test URL").should("not.exist")
      cy.contains("Test Attach").should("not.exist")

      cy.reload()
      cy.contains("From Cypress").click()
      cy.contains("Media").click()
      cy.contains("Test URL").should("not.exist")
      cy.contains("Test Attach").should("not.exist")
    })
  })
})
