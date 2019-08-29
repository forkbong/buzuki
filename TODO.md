# TODO

Notes for not yet implemented things.

## Greeklish search in song bodies with elasticsearch

We don't use elasticsearch anymore but for completeness, we should index
`greeklish_body`. We need a greeklish analyzer, with the default
tokenizer and not the `slug_tokenizer`.

## Improve song form validation

Remove `novalidate` from song form and implement meaningful client side
validation with bootstrap errors for required fields instead of the
default browser popup.

## Include only the necessary bootstrap

https://stackoverflow.com/a/47251052

## Enable brotli compression

https://medium.com/oyotech/how-brotli-compression-gave-us-37-latency-improvement-14d41e50fee4
https://computingforgeeks.com/how-to-enable-gzip-brotli-compression-for-nginx-on-linux/

## List of online tests

- https://html5.validator.nu/
- https://tools.pingdom.com/
- https://web.dev/
- https://www.ssllabs.com/ssltest/
