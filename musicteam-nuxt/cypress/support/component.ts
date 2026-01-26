// ***********************************************************
// This example support/component.ts is processed and
// loaded automatically before your test files.
//
// This is a great place to put global configuration and
// behavior that modifies Cypress.
//
// You can change the location of this file or turn off
// automatically serving support files with the
// 'supportFile' configuration option.
//
// You can read more here:
// https://on.cypress.io/configuration
// ***********************************************************

// Import commands.js using ES2015 syntax:
import "./commands"

import { ref, type Ref } from "vue"
import { mount } from "cypress/vue"

// Augment the Cypress namespace to include type definitions for
// your custom command.
// Alternatively, can be defined in cypress/support/component.d.ts
// with a <reference path="./component" /> at the top of your spec.
declare global {
  namespace Cypress {
    interface Chainable {
      mount: typeof mount
      mountVModel(
        componentDef: any,
        initModelValue: any,
        props?: Record<string, any>,
      ): Chainable<void>
      setModel(newV: any): Chainable<void>
      getModel(): Chainable<any>
    }
  }
}

Cypress.Commands.add("mount", mount)

Cypress.Commands.add("mountVModel", (componentDef, initModelValue, props = {}) => {
  const component = ref<any>()
  const model = ref(initModelValue)

  cy.mount(componentDef, {
    props: {
      ...props,
      modelValue: model.value,
      "onUpdate:modelValue": (newV) => {
        model.value = newV
        component.value.setProps({ modelValue: newV })
      },
    },
  })
    .then(({ wrapper }) => {
      component.value = wrapper
      return wrapper
    })
    .as("component")
  cy.wrap(model).as("model")
})

Cypress.Commands.add("setModel", (newV) => {
  cy.get("@component").then((component: any) => {
    component.setProps({ modelValue: newV })
  })
  cy.get("@model").then((model: any) => {
    model.value = newV
  })
})

Cypress.Commands.add("getModel", () => {
  return cy.get("@model").its("value")
})
