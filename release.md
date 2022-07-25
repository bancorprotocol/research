# Release Process

## 0. Pre-Release Checklist
Before starting the release process, verify the following:
* All work required for this release has been completed and the team is ready to release.
* [All Github Actions tests are green on main](https://github.com/bancorprotocol/research/actions?query=branch%3Amain).
* The [Netlify build](https://api.netlify.com/api/v1/badges/b4173988-e380-443b-94b1-78918e13a013/deploy-status) for "latest" is marked as passed. To avoid mysterious errors, best practice is to empty your browser cache when reading new versions of the docs!
* The [public documentation for the "latest" branch](https://simulator.bancor.network/chapters/bancor-research.html) looks correct, and the [release notes](https://github.com/bancorprotocol/research/releases) includes the last change which was made on main.
* Get agreement on the version number to use for the release.

#### Version Numbering

EvalML uses [semantic versioning](https://semver.org/). Every release has a major, minor and patch version number, and are displayed like so: `<majorVersion>.<minorVersion>.<patchVersion>`.

If you'd like to create a development release, which won't be deployed to pypi and conda and marked as a generally-available production release, please add a "dev" prefix to the patch version, i.e. `X.X.devX`. Note this claims the patch number--if the previous release was `0.12.0`, a subsequent dev release would be `0.12.dev1`, and the following release would be `0.12.2`, *not* `0.12.1`. Development releases deploy to [test.pypi.org](https://test.pypi.org/project/evalml/) instead of to [pypi.org](https://pypi.org/project/evalml).

## 1. Freeze `main` and run perf tests
After confirming the release is ready to go in step 0, we'll freeze the `main` branch and kick off the release performance tests.

Once a perf test document has been reviewed and approved by the team, we'll move forward with the release.

## 2. Create release PR to update version and release notes
Please use the following pattern for the release PR branch name: "release_vX.X.X". Doing so will bypass our release notes checkin test which requires all other PRs to add a release note entry.

Create a release PR with the following changes:
* Update `setup.py` and `bancor_research/__init__.py` to bump `__version__` to the new version.
* Populate the release PR body with a copy of this release's release notes, reformatted to [GitHub markdown](https://guides.github.com/features/mastering-markdown/). You'll reuse this text in step 2. You can generate the markdown by running `format_release_notes.sh` locally.
* Confirm that all release items are in the release notes under the correct header, and that no extra items are listed. You may have to do an "empty cache and hard reset" in your browser to see updates.


Checklist before merging:
* PR has been reviewed and approved.
* All tests are currently green on checkin and on main.
* The Jupyter Books build for the release PR branch has passed, and the resulting docs contain the expected release notes.
* Confirm with the team that `main` will be frozen until step 3 (github release) is complete.

Merge the release PR.

After merging, verify again that Jupyter Books "latest" is correct.

## 3. Create GitHub Release
After the release pull request has been merged into the main branch, it is time to draft the GitHub release. [Here's GitHub's documentation](https://help.github.com/en/github/administering-a-repository/managing-releases-in-a-repository#creating-a-release) on how to do that. Include the following when creating the release:
* The target should be the main branch, which is the default value.
* The tag should be the version number with a "v" prefix (e.g. "vX.X.X").
* The release title is the same as the tag, "vX.X.X"
* The release description should be the full release notes updates for the release, reformatted as GitHub markdown (from the release PR body in step 1).

Note that by targeting `main`, there must be no new merges to `main` from the moment we merge the release PR to when we publish the new GitHub release. Otherwise, the release will point at the wrong commit on `main`!

Save the release as a draft and make sure it looks correct. You could start the draft while waiting for the release PR to be ready to merge.

When it's ready to go, hit "Publish release." This will create a "vX.X.X" tag for the release, which tells Jupyter Books to build and update the "stable" version. This will also deploy the release [to pypi](https://pypi.org/project/evalml/), making it publicly accessible!

## 4. Make Documentation Public for Release Version
Creating the GitHub release should have updated the default `stable` docs branch to point at the new version. You'll now need to activate the new release version on Jupyter Books so its publicly visible in the list of versions. This is important so users can view old documentation versions which match their installed version.

Please do the following:
* Log in to our Netlify account and go [here](https://app.netlify.com/sites/incandescent-kelpie-250f0e/deploys) to view the deployments list.
* Find "vX.X.X" in the version list, and click "Edit" on the right.
* Check the "Active" checkbox and set privacy level to "Public", then click "Save"
* Verify "vX.X.X" is now visible as a version on our [docs](simulator.bancor.network) page. You may have to do an "empty cache and hard reset" in your browser to see updates.
* Verify "stable" corresponds with the new version, which should've been done in step 2.

## 5. Verify the release package has been deployed
Now that the release has been made in the repo, to pypi and in our documentation, the final step is making sure the new release is publicly pip-installable via pypi.

In a fresh virtualenv, install bancor-research via pip and ensure it installs successfully:
```shell
# should come back empty
pip freeze | grep bancor-research

pip install bancor-research
python --version
# should now list the correct version
python -c "import bancor_research; print(bancor_research.__version__)"
pip freeze | grep bancor-research
```

Note: make sure when you do this that you're in a virtualenv, your current working directory isn't in the evalml repo, and that you haven't added your repo to the `PYTHONPATH`, because in both cases python could pick up the repo instead, even in a virtualenv.

```
