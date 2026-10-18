// ***********************************************************
// This example support/e2e.ts is processed and
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

import "cypress-recurse/commands"

declare global {
  namespace Cypress {
    type RecurseOptions<T> = import("cypress-recurse").RecurseOptions<T>

    interface Chainable {
      recurse<T>(
        commandsFn: () => Chainable<T>,
        checkFn: (x: T, reducedValue?: any) => boolean | void | Chai.Assertion,
        options?: Partial<RecurseOptions<T>>,
      ): Chainable<T>
    }
  }
}

// Import commands.js using ES2015 syntax:
import "./commands.js"
