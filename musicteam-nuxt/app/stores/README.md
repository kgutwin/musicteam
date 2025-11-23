# Data Caching using Pinia Stores

The MusicTeam API backend is designed for somewhat modest (slow)
latency, in order to prioritize cost savings and enable a
scale-to-zero architecture. This means that the frontend needs to have
a robust caching strategy to ensure the app performs responsively
overall. This is implemented using [Pinia](https://pinia.vuejs.org),
which provides a lightweight and reactive data storage framework.

## Overview

The general approach uses `createStoreState()` defined in `index.ts`,
which takes an async "fetcher" function with no parameters and returns
a function that Pinia can use to define the structure of a store.

The store structure includes a `get()` function which returns a
promise to the result of the fetcher function. This result value is
stored in the store, and so subsequent calls to `get()` return the
cached data without re-invoking the fetcher. The `get()` function also
includes error handling, both through `useToaster()` which shows an
error message to the user, as well as storing the error value in a
separate property if needed.

The structure also includes a computed property named `data` which
invokes the `get()` function automatically and asynchronously. This
allows for direct use of fetched data in reactive contexts without
needing to have separate logic for managing the data fetch.

When data needs to be reloaded, the store state has two functions
available. The `refresh()` function schedules a re-fetch of the data
in the background, leaving the existing data in place until
overwritten by the new fetch result. The `expire()` function empties
the contents of the store, and resets it back to the initial "idle"
state. If `expire()` is called while store data is being used in a
reactive context, the data will appear to reset to the loading state,
but will begin reloading immediately.

## Parameter Stores

The approach described above is suitable for top-level resources that
require no parameters. Since many of the API resources are
parametrized by a parent resource ID, the `createParamStoreState()`
function is available to meet this need.

`createParamStoreState()` takes a "fetcher" function just like
`createStoreState()`, but this function can have parameters as defined
by an object. The `get()` function is available in this store, taking
an object with the desired parameter values. Those values are
JSON-encoded and used as a key into a mapping to the store state
defined by `createStoreState()`. When `get()` is called a subsequent
time with the same parameter values, the existing store state will be
returned. Since parameters are required, the computed property `data`
is not supported at the top level of `createParamStoreState()`.
However, it can be used on the return value of the `get()` function.

Reloading data stored by a `createParamStoreState()` is done using the
`refresh()` method. This method takes a set of optional parameters; if
provided, only the stores that match the parameter values will be
refreshed. Otherwise, all associated stores will be refreshed.
