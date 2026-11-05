describe("recordings", () => {
  beforeEach(() => {
    cy.login()
    cy.wipe()
    cy.prep("setlistComplete")
  })

  context("upload a recording", () => {
    beforeEach(() => {
      cy.get("@prep.setlist").then((id) => {
        cy.visit(`/setlists/${id}`)
        cy.exists("Test Title")
      })
      cy.contains("Recording").click()
      cy.dataCy("open-upload").click()
      cy.dataCy("file").selectFile("cypress/fixtures/test.mp3")

      cy.get("audio")
        .its("0.readyState")
        .should("equal", HTMLMediaElement.HAVE_ENOUGH_DATA)
      cy.get("audio").its("0.currentTime").should("equal", 0)

      // mute so we don't blast ourselves
      cy.get("audio").then(($el) => {
        $el.prop("muted", true)
      })

      // at least once, the test was fast enough that the canvas click
      // preceded the waveform load. We could probably add a sentinel
      // somewhere to register that the waveform has loaded, but for
      // now this should suffice.
      cy.wait(100)
    })

    context("creating a song mark", () => {
      beforeEach(() => {
        // click on waveform
        cy.get("canvas.recording-waveform").click()
        cy.get("audio").its("0.currentTime").should("be.within", 0.53, 0.55)

        // add a mark
        cy.dataCy("add-mark").click()
        cy.contains("Song One").click()

        cy.get(".recording-mark").within(() => {
          cy.exists(["0:00:00", "First", "Song One"])
        })
      })

      it("can click to seek", () => {
        cy.get("canvas.recording-waveform").click(15, 100)
        cy.get("audio").its("0.currentTime").should("be.within", 0.01, 0.02)

        cy.get(".recording-mark").within(() => {
          cy.contains("First").click()
        })
        // it will play to the end
        cy.get("audio").its("0.currentTime").should("be.within", 1.06, 1.13)
      })

      it("can nudge up and down", () => {
        cy.dataCy("nudge-up").click({ force: true })
        cy.get(".recording-mark").within(() => {
          cy.exists(["0:00:01"])
        })
        cy.dataCy("nudge-down").click({ force: true })
        cy.get(".recording-mark").within(() => {
          cy.exists(["0:00:00"])
        })
      })

      it("can go over to the song and play the recording there", () => {
        cy.get(".recording-mark").within(() => {
          cy.contains("Song One").click()
        })

        cy.exists(["CCLI Number", "Versions", "From Cypress"])
        cy.contains("Media").click()
        cy.exists(["Recordings", "1/4/2026"])
        cy.get("audio")
          .its("0.readyState")
          .should("equal", HTMLMediaElement.HAVE_ENOUGH_DATA)
        cy.get("audio").its("0.currentTime").should("be.within", 0.53, 0.55)
        cy.get("audio").then(($el) => {
          $el.prop("muted", true)
          $el.get(0).play()
        })
        cy.get("audio").its("0.currentTime").should("be.within", 1.06, 1.13)

        // rewind
        cy.wait(500)
        cy.dataCy("rewind").click()
        cy.get("audio").its("0.currentTime").should("be.within", 0.53, 0.55)

        // back to recording
        cy.dataCy("recording-setlist").click()
        cy.get("canvas.recording-waveform").should("exist")
      })

      it("can delete a mark", () => {
        cy.get(".recording-mark-delete").click({ force: true })
        cy.get(".recording-mark").should("not.exist")
      })
    })

    it("can add a non-song mark", () => {
      cy.get("canvas.recording-waveform").click(25, 120)
      cy.get("audio").its("0.currentTime").should("be.within", 0.001, 0.02)
      cy.dataCy("add-mark").click()
      cy.contains("Next").click()
      cy.get(".recording-mark").within(() => {
        cy.exists(["0:00:00", "Next"])
      })
    })

    it("can add an other mark", () => {
      cy.get("canvas.recording-waveform").click(1300, 90, { force: true })
      cy.get("audio").its("0.currentTime").should("be.within", 1.0, 1.13)
      cy.dataCy("add-mark").click()
      cy.contains("Other").click()
      cy.get(".recording-mark").within(() => {
        cy.exists(["0:00:01"])
        cy.dataCy("editing").click({ force: true })
        cy.dataCy("editable-cue_title", "input").type("My Cue{enter}")
        cy.exists(["My Cue"])
      })
    })

    it("can zoom", () => {
      cy.get("canvas.recording-waveform").its("0.width").should("equal", 1370)
      cy.dataCy("zoom-out").click()
      cy.get("canvas.recording-waveform").its("0.width").should("equal", 1096)
      cy.dataCy("zoom-out").click()
      cy.get("canvas.recording-waveform").its("0.width").should("equal", 876)
      cy.dataCy("zoom-in").click()
      cy.get("canvas.recording-waveform").its("0.width").should("equal", 1095)
      cy.dataCy("zoom-in").click()
      cy.get("canvas.recording-waveform").its("0.width").should("equal", 1368)
    })

    it("can add a comment", () => {
      cy.dataCy("comments").click()
      cy.contains("Add Comment").click()
      cy.dataCy("post-comment").within(() => {
        cy.get("textarea").type("hello there")
        cy.contains("Post").click()
      })
      cy.exists(["hello there"])
    })

    it("can delete the recording", () => {
      cy.dataCy("delete-recording").click()
      cy.exists(["No recordings uploaded yet"])
    })
  })
})
