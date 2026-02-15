// @ts-ignore
import MtSelectOther from "../../../app/components/mt/MtSelectOther.vue"

describe("<MtSelectOther />", () => {
  beforeEach(() => {
    cy.viewport(450, 150)
  })

  context("basic usage", () => {
    beforeEach(() => {
      cy.mountVModel(MtSelectOther, undefined, {
        options: ["First", "Second", "Third"],
      })
    })
    it("can select a choice", () => {
      cy.get("select").select("Second")
      cy.getModel().should("eq", "Second")
    })

    it("can select other", () => {
      cy.get("select").select("Other...")
      cy.get("input").type("flarb")
      cy.getModel().should("eq", "flarb")
    })

    it("can handle when the other box becomes empty", () => {
      cy.get("select").select("Other...")
      cy.get("input").type("fla{backspace}{backspace}{backspace}")
      cy.get("select").should("have.value", "Other...")
      cy.getModel().should("eq", "")
    })

    it("can change between other and options", () => {
      cy.get("select").select("Other...")
      cy.get("input").type("flarb")
      cy.get("select").select("Third")
      cy.getModel().should("eq", "Third")

      // when going back to Other, the previous text is gone
      cy.get("select").select("Other...")
      cy.get("input").should("have.value", "").type("fleeb")
      cy.getModel().should("eq", "fleeb")
    })

    it("can load an option as a value", () => {
      cy.setModel("Second")
      cy.get("select").should("have.value", "Second")
      cy.get("input").should("not.exist")
    })

    it("can load another value as a value", () => {
      cy.setModel("flarb")
      cy.get("select").should("have.value", "Other...")
      cy.get("input").should("have.value", "flarb")
    })
  })

  context("with initial value", () => {
    it("can start with an option as a value", () => {
      cy.mountVModel(MtSelectOther, "First", { options: ["First", "Second", "Third"] })

      cy.get("select").should("have.value", "First")
      cy.get("input").should("not.exist")
    })

    it("can start with another value as a value", () => {
      cy.mountVModel(MtSelectOther, "flarb", { options: ["First", "Second", "Third"] })

      cy.get("select").should("have.value", "Other...")
      cy.get("input").should("have.value", "flarb")
    })
  })
})
