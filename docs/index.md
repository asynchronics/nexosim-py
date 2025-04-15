---
hide:
    - navigation
---
{%
    include-markdown "../README.md"
    start="<!-- index start -->"
    end="<!-- index end -->"
%}

## Example

Here's a minimal example with a simple server implementation:

=== "Client"
    {%
        include-markdown "../README.md"
        start="<!-- example client start -->"
        end="<!-- example client end -->"
    %}

=== "Server"
    {%
        include-markdown "../README.md"
        start="<!-- example server start -->"
        end="<!-- example server end -->"
    %}

## Learn more

<div class="grid cards" markdown>

-   [:material-book-open-variant:{ .lg } **User Guide**](user_guide.md)

    ---
    The user guide contains information on general usage of the interface.
    If you are new to NeXosim-py, we recommend you start here.

-   [:material-code-brackets:{ .lg .middle } **API Reference**](reference/mod_root.md)

    ---

    A detailed description of the NeXosim-py API can be found here.

</div>