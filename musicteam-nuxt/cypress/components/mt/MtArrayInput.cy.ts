// @ts-ignore
import MtArrayInput from "../../../app/components/mt/MtArrayInput.vue"

describe("<MtArrayInput />", () => {
  beforeEach(() => {
    cy.viewport(450, 150)
  })

  context("basic usage", () => {
    beforeEach(() => {
      cy.mountVModel(MtArrayInput, [])
    })

    it("can enter a single value", () => {
      cy.get(".inp-array-newtag").type("foo ")
      cy.getModel().should("deep.eq", ["foo"])
    })

    it("can enter a value and blur", () => {
      cy.get(".inp-array-newtag").type("foo")
      cy.get(".inp-array-newtag").blur()
      cy.getModel().should("deep.eq", ["foo"])
    })

    it("can enter multiple values", () => {
      cy.get(".inp-array-newtag").type("foo bar baz ")
      cy.getModel().should("deep.eq", ["foo", "bar", "baz"])
    })

    it("can enter values and then delete them", () => {
      cy.get(".inp-array-newtag").type("foo bar {backspace}")
      cy.getModel().should("deep.eq", ["foo"])
    })

    it("can start with a value", () => {
      cy.setModel(["boo", "there"])
      cy.get(".inp-array-newtag").type("bla ")
      cy.getModel().should("deep.eq", ["boo", "there", "bla"])
    })

    it("can add a value at the beginning", () => {
      cy.setModel(["boo", "there"])
      cy.get(".inp-array-inserttag").first().type("new ", { force: true })
      cy.getModel().should("deep.eq", ["new", "boo", "there"])

      // and put in another value
      cy.focused().type("two ")
      cy.getModel().should("deep.eq", ["new", "two", "boo", "there"])
    })

    it("can backspace all values", () => {
      cy.setModel(["one", "two", "three"])
      cy.get(".inp-array-newtag").type("{backspace}")
      cy.focused().type("{backspace}")
      cy.focused().type("{backspace}")
      cy.getModel().should("deep.eq", [])
    })

    it("can move cursor and delete", () => {
      cy.setModel(["one", "two", "three"])
      cy.get(".inp-array-newtag").type("{leftArrow}")
      cy.focused().should("include.text", "three")
      cy.focused().type("{leftArrow}")
      cy.focused().type("{leftArrow}")
      cy.focused().should("include.text", "two")
      cy.focused().type("{backspace}")
      cy.getModel().should("deep.eq", ["one", "three"])
    })

    it("can click remove buttons", () => {
      cy.setModel(["one"])
      cy.get(".remove").click({ force: true })
      cy.getModel().should("deep.eq", [])

      cy.get(".inp-array-newtag").type("alpha beta charlie ")
      cy.get(".remove").last().click({ force: true })
      cy.get(".remove").first().click({ force: true })
      cy.getModel().should("deep.eq", ["beta"])
    })
  })

  context("allow space or comma", () => {
    it("allows space", () => {
      cy.mountVModel(MtArrayInput, [], { allowSpace: true })
      cy.get(".inp-array-newtag").type("Joe Smith,Jane Doe{enter}")
      cy.getModel().should("deep.eq", ["Joe Smith", "Jane Doe"])
    })

    it("allows space and comma", () => {
      cy.mountVModel(MtArrayInput, [], { allowSpace: true, allowComma: true })
      cy.get(".inp-array-newtag").type("First, good{enter}also, good{enter}")
      cy.getModel().should("deep.eq", ["First, good", "also, good"])
    })
  })

  context("can be disabled", () => {
    it("can be disabled", () => {
      cy.mountVModel(MtArrayInput, ["one", "two", "three"], { disabled: true })
      cy.get(".inp-array-newtag").type("xyz{enter}", { force: true })
      cy.get(".inp-array-inserttag").first().type("xyz{enter}", { force: true })
      cy.get(".inp-array-newtag").type("{backspace}", { force: true })
      cy.get(".inp-array-inserttag").last().type("{backspace}", { force: true })
      cy.get(".inp-array-el").first().type("{backspace}", { force: true })
      cy.getModel().should("deep.eq", ["one", "two", "three"])
      cy.contains("xyz").should("not.exist")
      cy.get(".remove").should("not.exist")
    })
  })
})
